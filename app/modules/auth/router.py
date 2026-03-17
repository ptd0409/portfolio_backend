import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
#from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    create_verify_email_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_async_session
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MeResponse,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.email_service import send_reset_password_email, send_verify_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


async def send_verify_email_safe(email: str, verify_link: str) -> None:
    try:
        await send_verify_email(email, verify_link)
    except Exception:
        logger.exception("Failed to send verification email to %s", email)


async def send_reset_password_email_safe(email: str, reset_link: str) -> None:
    try:
        await send_reset_password_email(email, reset_link)
    except Exception:
        logger.exception("Failed to send reset password email to %s", email)


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
#@limiter.limit("3/10minutes")
async def register(
    #request: Request,
    #response: Response,
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    email = payload.email.strip().lower()

    verified_admin_count_result = await session.execute(
        select(func.count()).select_from(User).where(
            User.role == "admin",
            User.is_verified.is_(True),
        )
    )
    verified_admin_count = verified_admin_count_result.scalar_one()

    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        verify_token = create_verify_email_token(email)
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"
        background_tasks.add_task(send_verify_email_safe, email, verify_link)

        return MessageResponse(
            message="Account already exists but is not verified. A verification email has been resent."
        )

    if verified_admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled",
        )

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role="admin",
        is_active=True,
        is_verified=False,
        failed_login_attempts=0,
    )
    session.add(user)
    await session.commit()

    verify_token = create_verify_email_token(email)
    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"
    background_tasks.add_task(send_verify_email_safe, email, verify_link)

    return MessageResponse(
        message="Registration successful. Please check your email to verify your account."
    )


@router.post("/resend-verification", response_model=MessageResponse)
#@limiter.limit("3/10minutes")
async def resend_verification(
    #request: Request,
    #response: Response,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    email = payload.email.strip().lower()

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user and not user.is_verified and user.is_active:
        verify_token = create_verify_email_token(email)
        verify_link = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"
        background_tasks.add_task(send_verify_email_safe, email, verify_link)

    return MessageResponse(
        message="If the account exists and is not verified, a verification email has been sent."
    )


@router.post("/verify-email", response_model=MessageResponse)
#@limiter.limit("10/10minutes")
async def verify_email(
    #request: Request,
    #response: Response,
    payload: VerifyEmailRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        token_payload = decode_token(payload.token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    if token_payload.get("type") != "verify_email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    email = token_payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        return MessageResponse(message="Email is already verified")

    user.is_verified = True
    await session.commit()

    return MessageResponse(message="Email verified successfully")


@router.post("/login", response_model=TokenResponse)
#@limiter.limit("5/minute")
async def login(
    #request: Request,
    #response: Response,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    email = payload.email.strip().lower()

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been disabled",
        )

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="This account is temporarily locked. Please try again later",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in",
        )

    if not verify_password(payload.password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            user.failed_login_attempts = 0

        await session.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)

    access_token = create_access_token(subject=user.email, role=user.role)
    refresh_token_value = create_refresh_token()
    refresh_token_hashed = hash_refresh_token(refresh_token_value)

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hashed,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )
    session.add(refresh_token)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
    )


@router.post("/refresh", response_model=TokenResponse)
#@limiter.limit("10/minute")
async def refresh_access_token(
    #request: Request,
    #response: Response,
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_async_session),
):
    incoming_token_hash = hash_refresh_token(payload.refresh_token)

    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == incoming_token_hash)
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    result = await session.execute(select(User).where(User.id == stored_token.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or not found",
        )

    access_token = create_access_token(subject=user.email, role=user.role)
    new_refresh_token_value = create_refresh_token()
    new_refresh_token_hash = hash_refresh_token(new_refresh_token_value)

    stored_token.revoked_at = datetime.now(timezone.utc)

    new_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )
    session.add(new_refresh_token)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token_value,
    )


@router.post("/logout", response_model=MessageResponse)
#@limiter.limit("20/minute")
async def logout(
    #request: Request,
    #response: Response,
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_async_session),
):
    incoming_token_hash = hash_refresh_token(payload.refresh_token)

    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == incoming_token_hash)
    )
    stored_token = result.scalar_one_or_none()

    if stored_token and stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.now(timezone.utc)
        await session.commit()

    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=MeResponse)
#@limiter.limit("30/minute")
async def me(
    #request: Request,
    #response: Response,
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_async_session),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )

    token = authorization.replace("Bearer ", "").strip()

    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return MeResponse(
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        is_active=user.is_active,
    )


@router.post("/forgot-password", response_model=MessageResponse)
#@limiter.limit("3/10minutes")
async def forgot_password(
    #request: Request,
    #response: Response,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    email = payload.email.strip().lower()

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user and user.is_verified and user.is_active:
        token = create_reset_token(user.email)
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        background_tasks.add_task(send_reset_password_email_safe, user.email, reset_link)

    return MessageResponse(
        message="If this email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
#@limiter.limit("5/10minutes")
async def reset_password(
    #request: Request,
    #response: Response,
    payload: ResetPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        token_payload = decode_token(payload.token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if token_payload.get("type") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    email = token_payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.password_hash = hash_password(payload.new_password)

    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        )
    )
    active_tokens = result.scalars().all()

    now = datetime.now(timezone.utc)
    for token_row in active_tokens:
        token_row.revoked_at = now

    user.failed_login_attempts = 0
    user.locked_until = None

    await session.commit()

    return MessageResponse(message="Password has been reset successfully")