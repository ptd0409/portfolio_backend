## Generate JWT secret key

python -c "import secrets; print(secrets.token_urlsafe(64))"
