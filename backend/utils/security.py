# backend/utils/security.py
import os
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")  # Cambiar en producción
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", b'DIyMqNEZcjdCmqMaQUL5x1Ycxo6iO5QfrrtAXdbxXi4=')  # 32 bytes
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
cipher = Fernet(ENCRYPTION_KEY)

# Usuarios (cargados desde .env)
USERS = {}
for key, value in os.environ.items():
    if key.startswith("USER_"):
        username = key[5:].lower()  # Quitar "USER_" y convertir a minúsculas
        USERS[username] = pwd_context.hash(value)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    if username in USERS and verify_password(password, USERS[username]):
        return username
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return cipher.decrypt(encrypted_data.encode()).decode()

# backend/utils/__init__.py
from .security import *