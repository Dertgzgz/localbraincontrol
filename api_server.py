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
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sse_starlette.sse import EventSourceResponse
from google import genai

# Importar lógica existente
from sys_hardware_monitor import get_gpu_stats, get_ollama_data
from i18n import TRANSLATIONS, t
from ai_agent_core import ejecutar_agente_local_async
from langchain_core.messages import HumanMessage, AIMessage
from huggingface_service import hf_service

load_dotenv()

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
async def chat_endpoint(request: ChatRequest):
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
                    api_key = json.load(f).get("google")
        
        if not api_key:
            return [{"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash (Tier Libre)"}]

        client = genai.Client(api_key=api_key)
        models = client.models.list()
        return [{"id": m.name.split("/")[-1], "name": m.display_name} for m in models if "generateContent" in m.supported_generation_methods]
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
async def analyze_logs_endpoint(request: Dict):
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
                        api_key = json.load(f).get("google")
            
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
async def save_credentials(req: CredentialRequest):
    # TODO: Implementar encriptación de credenciales para mayor seguridad
    os.makedirs("config", exist_ok=True)
    path = "config/credentials.json"
    creds = {}
    if os.path.exists(path):
        with open(path, "r") as f: creds = json.load(f)
    creds[req.provider] = req.key
    with open(path, "w") as f: json.dump(creds, f)
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
async def save_session(request: Request):
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
    # Gemini analiza el hardware y sugiere parámetros
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
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            path = "config/credentials.json"
            if os.path.exists(path):
                with open(path, "r") as f: api_key = json.load(f).get("google")
        
        if not api_key: raise HTTPException(status_code=401, detail="Google API Key required for optimization")
            
        client = genai.Client(api_key=api_key)
        res = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        
        # Extraer JSON de la respuesta
        import re
        match = re.search(r"\{[\s\S]*\}", res.text)
        if match:
            suggestion = json.loads(match.group(0))
            return suggestion
        return {"error": "Could not parse AI suggestion"}
    except Exception as e:
        logger.error(f"Error in optimization: {e}")
        return {"error": str(e)}

@app.get("/api/huggingface/search")
async def search_hf_models(q: str): return await hf_service.search_models(q)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
