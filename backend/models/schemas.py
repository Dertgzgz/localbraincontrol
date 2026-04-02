# backend/models/__init__.py
from .schemas import *

# backend/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class HardwareMetrics(BaseModel):
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    gpu: Optional[Dict] = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    prompt: str = Field(..., max_length=10000)  # Limitar longitud del prompt
    history: List[Message] = []
    lang: str = Field("es", pattern="^(es|en|eu)$")  # Solo idiomas soportados

class PullRequest(BaseModel):
    name: str

class CredentialRequest(BaseModel):
    provider: str
    key: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str