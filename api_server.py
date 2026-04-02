import os
import sys
import psutil
import asyncio
import logging
import httpx
import json
import uuid
import time
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sse_starlette.sse import EventSourceResponse
from google import genai
from cryptography.fernet import Fernet
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Importar lógica existente
from sys_hardware_monitor import get_gpu_stats, get_ollama_data
from i18n import TRANSLATIONS, t
from ai_agent_core import ejecutar_agente_local_async
from langchain_core.messages import HumanMessage, AIMessage
from huggingface_service import hf_service
from modelscope_service import modelscope_service

load_dotenv()

# Configuración de Seguridad
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

# Funciones de Seguridad
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

# Persistencia de Uso
USAGE_FILE = "config/usage_stats.json"
def load_usage():
    try:
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"tokens_consumed": 0, "requests_count": 0, "last_update": ""}

def save_usage(stats):
    try:
        os.makedirs("config", exist_ok=True)
        stats["last_update"] = str(asyncio.get_event_loop().time())
        with open(USAGE_FILE, "w") as f:
            json.dump(stats, f)
    except (OSError, json.JSONEncodeError):
        pass

def track_usage(tokens: int):
    stats = load_usage()
    stats["tokens_consumed"] += tokens
    stats["requests_count"] += 1
    save_usage(stats)

# Configuración de Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("APIServer")

app = FastAPI(title="Antigravity Local AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de Datos
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

# Seguridad
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Rutas de Autenticación
@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    user_auth = authenticate_user(user.username, user.password)
    if not user_auth:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Rutas
@app.get("/api/system/metrics", response_model=HardwareMetrics)
async def get_system_metrics():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        gpu = get_gpu_stats()
        return {
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_gb": ram.used / 1024**3,
            "ram_total_gb": ram.total / 1024**3,
            "gpu": gpu
        }
    except Exception as e:
        logger.error(f"Error en metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ollama/ps")
async def get_running_models(): return get_ollama_data("ps")

@app.get("/api/ollama/tags")
async def get_available_models(): return get_ollama_data("tags")

@app.get("/api/config/i18n")
async def get_all_translations(): return TRANSLATIONS

@app.post("/api/agent/chat")
async def chat_endpoint(request: ChatRequest, current_user: str = Depends(get_current_user)):
    langchain_history = []
    for msg in request.history:
        langchain_history.append(HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content))
            
    async def event_generator():
        try:
            mem = psutil.virtual_memory()
            sys_ctx = {"os": sys.platform, "cpu_threads": psutil.cpu_count(), "ram_total_gb": round(mem.total / (1024**3), 2), "gpu": "Detected"}
            async for chunk in ejecutar_agente_local_async(request.prompt, langchain_history, sys_context=sys_ctx):
                yield {"data": chunk}
        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield {"data": json.dumps({"type": "error", "content": str(e)})}
    return EventSourceResponse(event_generator())

@app.get("/api/models/google")
async def list_google_models():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            path = "config/credentials.json"
            if os.path.exists(path):
                with open(path, "r") as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = decrypt_data(encrypted_data)
                        creds = json.loads(decrypted_data)
                        api_key = creds.get("google")
        
        if not api_key:
            return [{"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Tier Libre)"}]

        client = genai.Client(api_key=api_key)
        models = client.models.list()
        result = []
        for m in models:
            try:
                # Intentar el método antiguo
                if hasattr(m, 'supported_generation_methods') and "generateContent" in m.supported_generation_methods:
                    result.append({"id": m.name.split("/")[-1], "name": m.display_name})
                elif hasattr(m, 'supported_actions') and "generateContent" in m.supported_actions:
                    result.append({"id": m.name.split("/")[-1], "name": m.display_name})
                else:
                    # Si no tiene el atributo, asumir que es un modelo generativo
                    result.append({"id": m.name.split("/")[-1], "name": m.display_name})
            except AttributeError:
                # Fallback: incluir todos los modelos Gemini
                if "gemini" in m.name.lower():
                    result.append({"id": m.name.split("/")[-1], "name": m.display_name})
        return result
    except Exception as e:
        logger.error(f"Error listing Google models: {e}")
        return [{"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Default)"}]

@app.get("/api/system/usage")
async def get_usage_stats(): return load_usage()

@app.get("/api/logs/peek")
async def peek_logs(source: str = "app", lines: int = 20):
    rutas = {
        "app": os.path.join(os.path.dirname(__file__), "logs", "app_local.log"),
        "mcp": os.path.join(os.path.dirname(__file__), "logs", "mcp_server.log"),
        "backend": os.path.join(os.path.dirname(__file__), "logs", "backend.log"),
        "frontend": os.path.join(os.path.dirname(__file__), "logs", "frontend.log"),
        "ollama": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "server.log")
    }
    ruta = rutas.get(source.lower())
    if not ruta or not os.path.exists(ruta): return {"content": "Log not found"}
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            content = "".join(f.readlines()[-lines:])
            return {"content": content}
    except: return {"content": "Error reading log"}

@app.post("/api/logs/analyze")
async def analyze_logs_endpoint(request: Dict, current_user: str = Depends(get_current_user)):
    source = request.get("source", "app")
    agent_id = request.get("agent", "gemini-1.5-flash")
    lines = request.get("lines", 100)
    
    rutas = {
        "app": os.path.join(os.path.dirname(__file__), "logs", "app_local.log"),
        "mcp": os.path.join(os.path.dirname(__file__), "logs", "mcp_server.log"),
        "backend": os.path.join(os.path.dirname(__file__), "logs", "backend.log"),
        "frontend": os.path.join(os.path.dirname(__file__), "logs", "frontend.log"),
        "ollama": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "server.log")
    }
    ruta = rutas.get(source.lower())
    if not ruta or not os.path.exists(ruta): raise HTTPException(status_code=404, detail="Log source not found")
        
    try:
        with open(ruta, "r", encoding="utf-8", errors="replace") as f:
            log_data = "".join(f.readlines()[-lines:])
            
        prompt = f"{t('devops_prompt')}\n--- LOG ---\n{log_data}"
        
        if agent_id == "qwen":
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0)
            res = await llm.ainvoke([HumanMessage(content=prompt)])
            dictamen = res.content
        else:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                path = "config/credentials.json"
                if os.path.exists(path):
                    with open(path, "r") as f:
                        encrypted_data = f.read()
                        if encrypted_data:
                            decrypted_data = decrypt_data(encrypted_data)
                            creds = json.loads(decrypted_data)
                            api_key = creds.get("google")
            
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(model=agent_id, contents=prompt)
            dictamen = res.text
            if res.usage_metadata:
                track_usage(res.usage_metadata.total_token_count)
            
        return {"dictamen": dictamen, "raw_log": log_data}
    except Exception as e:
        logger.error(f"Error in log analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/capabilities")
async def get_system_capabilities():
    mem = psutil.virtual_memory()
    return {"os": sys.platform, "cpu_threads": psutil.cpu_count(), "ram_total_gb": round(mem.total / (1024**3), 2)}

@app.post("/api/config/credentials")
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

# --- Gestión de Sesiones de Chat ---
SESSIONS_DIR = "config/chat_sessions"

@app.get("/api/chat/sessions")
async def list_sessions():
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    sessions = []
    for f in os.listdir(SESSIONS_DIR):
        if f.endswith(".json"):
            try:
                with open(os.path.join(SESSIONS_DIR, f), "r") as s:
                    data = json.load(s)
                    sessions.append({
                        "id": f.replace(".json", ""), 
                        "title": data.get("title", f), 
                        "last_update": data.get("last_update")
                    })
            except: pass
    return sorted(sessions, key=lambda x: x.get("last_update", ""), reverse=True)

@app.get("/api/chat/sessions/{session_id}")
async def get_session(session_id: str):
    path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if not os.path.exists(path): raise HTTPException(status_code=404)
    with open(path, "r") as f: return json.load(f)

@app.post("/api/chat/sessions/save")
async def save_session(request: Request, current_user: str = Depends(get_current_user)):
    data = await request.json()
    session_id = data.get("id") or str(uuid.uuid4())
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    data["id"] = session_id
    data["last_update"] = str(time.time())
    with open(path, "w") as f: json.dump(data, f)
    return {"id": session_id}

# --- Resolución de Contexto ---
@app.post("/api/context/resolve")
async def resolve_context(request: Request):
    data = await request.json()
    items = data.get("items", [])
    resolved = []
    for item in items:
        rtype = item.get("type")
        value = item.get("value")
        content = ""
        try:
            if rtype == "url":
                async with httpx.AsyncClient() as client:
                    resp = await client.get(value, timeout=10.0)
                    content = resp.text[:10000] 
            elif rtype == "file":
                if os.path.exists(value):
                    with open(value, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
            resolved.append({"type": rtype, "value": value, "content": content})
        except Exception as e:
            resolved.append({"type": rtype, "value": value, "content": f"Error: {str(e)}"})
    return {"resolved": resolved}

# --- Optimización y Tuning de Modelo ---
SETTINGS_FILE = "config/model_settings.json"

@app.get("/api/model/settings")
async def get_model_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f: return json.load(f)
    except: pass
    return {"num_ctx": 16384, "num_gpu": 100, "temperature": 0.0}

@app.post("/api/model/settings")
async def save_model_settings(request: Request):
    data = await request.json()
    os.makedirs("config", exist_ok=True)
    with open(SETTINGS_FILE, "w") as f: json.dump(data, f)
    return {"status": "saved"}

@app.post("/api/model/optimize")
async def optimize_model(request: Request):
    # Usar modelo local para analizar hardware y sugerir parámetros
    try:
        mem = psutil.virtual_memory()
        gpu = get_gpu_stats()
        
        hardware_info = {
            "ram_total_gb": mem.total / 1024**3,
            "ram_available_gb": mem.available / 1024**3,
            "cpu_threads": psutil.cpu_count(),
            "gpu": gpu
        }
        
        prompt = (
            "Analiza este hardware y sugiere la configuración óptima para un modelo LLM local (Ollama).\n"
            f"HARDWARE: {json.dumps(hardware_info)}\n"
            "Responde ÚNICAMENTE en formato JSON con estos campos:\n"
            "- num_ctx: int (tokens de contexto, ej 2048, 4096, 16384...)\n"
            "- num_gpu: int (capas en GPU, 0 a 100)\n"
            "- temperature: float (0.0 a 1.0)\n"
            "- reasoning: string (explicación breve de por qué estos valores para este PC en español)\n"
        )
        
        # Usar modelo local en lugar de Google Gemini
        sys_ctx = {"os": sys.platform, "cpu_threads": psutil.cpu_count(), "ram_total_gb": round(mem.total / (1024**3), 2), "gpu": "Detected"}
        
        response_text = ""
        async for chunk in ejecutar_agente_local_async(prompt, sys_context=sys_ctx):
            # El chunk viene en formato SSE: {"type": "text", "content": "..."}
            try:
                chunk_data = json.loads(chunk)
                if chunk_data.get("type") == "text":
                    response_text += chunk_data.get("content", "")
            except json.JSONDecodeError:
                # Si no es JSON válido, agregarlo directamente
                response_text += chunk
        
        logger.info(f"Respuesta concatenada del modelo local: {response_text}")
        
        # Extraer JSON de la respuesta
        import re
        match = re.search(r"\{[\s\S]*\}", response_text)
        if match:
            suggestion = json.loads(match.group(0))
            return suggestion
        return {"error": "Could not parse AI suggestion"}
    except Exception as e:
        logger.error(f"Error in optimization: {e}")
        return {"error": str(e)}

@app.get("/api/huggingface/search")
async def search_hf_models(q: str, limit: int = 10):
    try:
        return hf_service.search_models(q, limit)
    except Exception as e:
        logger.error(f"Error searching HF models: {e}")
        return []

@app.post("/api/huggingface/download")
async def download_hf_model(request: dict):
    repo_id = request.get("repoId")
    filename = request.get("filename")
    if not repo_id or not filename:
        return {"error": "repoId and filename required"}
    
    try:
        result = hf_service.download_and_register(repo_id, filename, "C:\\Users\\alber\\.ollama\\models")
        return result
    except Exception as e:
        logger.error(f"Error downloading HF model: {e}")
        return {"error": str(e)}

@app.get("/api/modelscope/search")
async def search_ms_models(q: str, limit: int = 10):
    try:
        return modelscope_service.search_models(q, limit)
    except Exception as e:
        logger.error(f"Error searching ModelScope: {e}")
        return []

@app.post("/api/modelscope/download")
async def download_ms_model(request: dict):
    model_id = request.get("modelId")
    if not model_id:
        return {"error": "modelId required"}
    
    try:
        result = modelscope_service.download_and_register(model_id, "C:\\Users\\alber\\.ollama\\models")
        return result
    except Exception as e:
        logger.error(f"Error downloading ModelScope model: {e}")
        return {"error": str(e)}

@app.post("/api/errors/log")
async def log_frontend_error(request: dict):
    """Endpoint para que el frontend registre errores"""
    error_data = request.get("error", {})
    component = request.get("component", "frontend")
    message = error_data.get("message", "Unknown error")
    stack = error_data.get("stack", "")
    url = error_data.get("url", "")
    line = error_data.get("line", 0)
    column = error_data.get("column", 0)

    # Log detallado
    logger.error(f"Frontend Error: {message}", extra={
        'component': component,
        'stack': stack,
        'url': url,
        'line': line,
        'column': column
    })

    return {"status": "logged"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
