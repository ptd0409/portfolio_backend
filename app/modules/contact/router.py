from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.models.contact_message import ContactMessage
from app.schemas.contact import ContactCreate
from app.services.email_service import send_contact_notification

router = APIRouter(prefix="/contact", tags=["contact"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    payload: ContactCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    contact = ContactMessage(
        name=payload.name,
        email=payload.email,
        message=payload.message
    )

    session.add(contact)

    try:
        await session.commit()
        await session.refresh(contact)
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save contact message",
        )

    background_tasks.add_task(
        send_contact_notification,
        payload.name,
        payload.email,
        payload.message
    )

    return {
        "message": "Contact message sent successfully",
        "data": {
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "message": contact.message,
            "created_at": contact.created_at.isoformat() if contact.created_at else None
        }
    }