import asyncio
import json
import os
import uuid
import re
import logging
from typing import List, AsyncGenerator
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from mcp_client_connector import get_mcp_client
from i18n import t
from knowledge_engine import get_knowledge_summary

logger = logging.getLogger("AgenteLocal")
logger.setLevel(logging.DEBUG)

class PatchedChatOllama(ChatOllama):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """Versión síncrona del parche."""
        logger.info(f"🧠 Invocando (sync) modelo con {len(messages)} mensajes.")
        result = super()._generate(messages, stop, run_manager, **kwargs)
        if result and result.generations:
            for gen in result.generations:
                self._patch_message(gen.message)
        return result

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        """Versión asíncrona del parche con seguridad."""
        logger.info(f"🧠 Invocando (async) modelo con {len(messages)} mensajes.")
        result = await super()._agenerate(messages, stop, run_manager, **kwargs)
        if result and result.generations:
            for gen in result.generations:
                self._patch_message(gen.message)
        return result

    def _patch_message(self, msg):
        """Lógica común para detectar herramientas en texto."""
        if not msg.tool_calls and msg.content:
            match = re.search(r"\{[\s\S]*\"name\"[\s\S]*\"arguments\"[\s\S]*\}", msg.content)
            if match:
                try:
                    data = json.loads(match.group(0))
                    if "name" in data and "arguments" in data:
                        logger.info(f"🛠️ Tool detectada: {data['name']}")
                        call_id = f"call_{uuid.uuid4().hex[:8]}"
                        msg.tool_calls = [{"name": data["name"], "args": data["arguments"], "id": call_id}]
                        msg.content = ""
                except json.JSONDecodeError:
                    pass

DANGEROUS_TOOLS = ["ejecutar_comando", "eliminar_archivo", "escribir_archivo"]

def get_llm():
    # Cargar configuración dinámica
    settings = {"num_ctx": 16384, "num_gpu": 100, "temperature": 0}
    try:
        if os.path.exists("config/model_settings.json"):
            with open("config/model_settings.json", "r") as f:
                settings.update(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    return PatchedChatOllama(
        model="qwen2.5-coder:3b", 
        temperature=settings["temperature"],
        num_ctx=settings["num_ctx"],
        num_gpu=settings["num_gpu"]
    )

async def ejecutar_agente_local_async(prompt: str, history: List[BaseMessage] = None, sys_context: dict = None) -> AsyncGenerator[str, None]:
    """Ejecución asíncrona optimizada para Qwen 2.5 Coder 3B con conciencia de hardware."""
    if history is None:
        history = []
        
    llm = get_llm()
    # Para el cliente MCP, necesitamos un loop asíncrono si no estamos en uno
    mcp_client = get_mcp_client()
    
    try:
        raw_tools = await mcp_client.get_tools()
        tools_map = {t.name: t for t in raw_tools}
    except Exception as e:
        yield json.dumps({"type": "error", "content": f"Error MCP: {e}"})
        return

    system_msg = (
        "Eres 'Antigravity Local', un sistema inteligente de IA AUTO-REPARABLE y experto DevOps.\n"
        "Tu misión no es solo asistir, sino VIGILAR la salud de esta propia aplicación.\n"
        "Cuentas con acceso real al sistema mediante estas HERRAMIENTAS:\n"
        + "\n".join([f"- {t.name}: {t.description}" for t in raw_tools]) + "\n\n"
        "REGLA CRITICA: Puedes leer tus propios logs (backend, frontend, mcp) para diagnosticar fallos.\n"
        "Si detectas un error en los logs, sugiere parches y usa herramientas para repararlos.\n"
    )

    if sys_context:
        system_msg += (
            "\nCONTEXTO DE RECURSOS DEL SISTEMA:\n"
            f"- OS: {sys_context.get('os')}\n"
            f"- CPU Threads: {sys_context.get('cpu_threads')}\n"
            f"- RAM Total: {sys_context.get('ram_total_gb')}GB\n"
            f"- GPU: {sys_context.get('gpu')}\n"
            "---\nAnaliza si el hardware es suficiente para lo que pida el usuario.\n"
        )
    
    system_msg += f"\n{t('sys_lang')}\n"
    system_msg += f"\n{get_knowledge_summary()}\n"
    
    llm_with_tools = llm.bind_tools(raw_tools)
    mensajes = [AIMessage(content=system_msg)] + history + [HumanMessage(content=prompt)]
    
    try:
        response = await llm_with_tools.ainvoke(mensajes)
        
        for _ in range(5):
            if not response.tool_calls:
                break
                
            for tool_call in response.tool_calls:
                t_name = tool_call['name']
                t_args = tool_call['args']
                
                if t_name in DANGEROUS_TOOLS:
                    # En la API, devolvemos un evento de "requiere aprobación"
                    yield json.dumps({
                        "type": "require_approval", 
                        "tool_call": tool_call,
                        "message": f"⚠️ Requiere aprobación para: `{t_name}`..." 
                    })
                    return
                
                if t_name not in tools_map:
                    mensajes.append(response)
                    mensajes.append(AIMessage(content=f"Error: La herramienta {t_name} no existe."))
                    continue

                result = await tools_map[t_name].ainvoke(t_args)
                mensajes.append(response)
                mensajes.append(AIMessage(content=f"RESULTADO DE {t_name}: {json.dumps(result)}"))
            
            response = await llm_with_tools.ainvoke(mensajes)

        if response.content:
            for word in response.content.split():
                yield json.dumps({"type": "text", "content": word + " "})
                await asyncio.sleep(0.02)
        else:
            yield json.dumps({"type": "text", "content": t("action_ok")})

    except Exception as e:
        logger.error(f"💥 Error en agente: {str(e)}")
        yield json.dumps({"type": "error", "content": f"Error técnico: {str(e)}"})

# Mantener compatibilidad con Streamlit (opcional, pero mejor refactorizar app_local.py luego)
def ejecutar_agente_local(prompt: str):
    import streamlit as st
    history = st.session_state.get("messages", [])
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Esto es un hack para streamlit, pero en FastAPI usaremos el async generator directamente
        async def collect():
            async for chunk in ejecutar_agente_local_async(prompt, history):
                data = json.loads(chunk)
                if data["type"] == "text":
                    yield data["content"]
                elif data["type"] == "require_approval":
                    st.session_state.pending_tool_call = data["tool_call"]
                    yield data["message"]
            
        for chunk in loop.run_until_complete(collect_async_generator(collect())):
            yield chunk
    finally:
        loop.close()

async def collect_async_generator(gen):
    chunks = []
    async for chunk in gen:
        chunks.append(chunk)
    return chunks
