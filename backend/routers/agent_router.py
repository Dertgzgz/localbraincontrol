# backend/routers/agent_router.py
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
import psutil
import sys
import json
from ..models.schemas import ChatRequest
from ..dependencies import get_current_user
from ..config import logger
from ai_agent_core import ejecutar_agente_local_async
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()

@router.post("/agent/chat")
async def chat_endpoint(request: ChatRequest, current_user: str = Depends(get_current_user)):
    langchain_history = []
    for msg in request.history:
        langchain_history.append(HumanMessage(content=msg.content) if msg.role == "user" else AIMessage(content=msg.content))
            
    async def event_generator():
        try:
            mem = psutil.virtual_memory()
            sys_ctx = {"os": sys.platform, "cpu_threads": psutil.cpu_count(), "ram_total_gb": round(mem.total / 1024**3, 2), "gpu": "Detected"}
            async for chunk in ejecutar_agente_local_async(request.prompt, langchain_history, sys_context=sys_ctx):
                yield {"data": chunk}
        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield {"data": json.dumps({"type": "error", "content": str(e)})}
    return EventSourceResponse(event_generator())