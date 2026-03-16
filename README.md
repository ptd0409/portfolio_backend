## Generate JWT secret key

openssl rand -hex 32

## Create migration init

alembic revision --autogenerate -m "init tables"
alembic upgrade head

## Generate Admin API key

openssl rand -hex 32
