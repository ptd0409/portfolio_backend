## Generate JWT secret key

python -c "import secrets; print(secrets.token_urlsafe(64))"

## Create migration init

alembic revision --autogenerate -m "init tables"
alembic upgrade head
