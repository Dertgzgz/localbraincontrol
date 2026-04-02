# backend/routers/config_router.py
from fastapi import APIRouter, Depends, HTTPException
import os
import json
from ..models.schemas import CredentialRequest
from ..dependencies import get_current_user
from ..utils.security import encrypt_data, decrypt_data
from ..config import logger

router = APIRouter()

@router.post("/config/credentials")
async def save_credentials(req: CredentialRequest, current_user: str = Depends(get_current_user)):
    os.makedirs("config", exist_ok=True)
    path = "config/credentials.json"
    creds = {}
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                encrypted_data = f.read()
                if encrypted_data:
                    decrypted_data = decrypt_data(encrypted_data)
                    creds = json.loads(decrypted_data)
        except Exception:
            pass  # Si falla, empezar con vacío
    creds[req.provider] = req.key
    encrypted_creds = encrypt_data(json.dumps(creds))
    with open(path, "w") as f:
        f.write(encrypted_creds)
    return {"status": "saved"}

@router.get("/config/i18n")
async def get_all_translations():
    from i18n import TRANSLATIONS
    return TRANSLATIONS

@router.get("/model/settings")
async def get_model_settings():
    try:
        SETTINGS_FILE = "config/model_settings.json"
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except:
        pass
    return {"num_ctx": 16384, "num_gpu": 100, "temperature": 0.0}

@router.post("/model/settings")
async def save_model_settings(request):
    data = await request.json()
    os.makedirs("config", exist_ok=True)
    SETTINGS_FILE = "config/model_settings.json"
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)
    return {"status": "saved"}