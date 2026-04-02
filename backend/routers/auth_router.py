# backend/routers/auth_router.py
from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta
from ..models.schemas import UserLogin, Token
from ..utils.security import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    user_auth = authenticate_user(user.username, user.password)
    if not user_auth:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}