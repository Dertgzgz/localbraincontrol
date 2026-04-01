import streamlit as st
import asyncio
import time
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys

st.set_page_config(page_title="Agente Local MCP", layout="wide")
st.title("Agente MCP Local - Gemini")

if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = []

# Guardar estado de herramienta pendiente de ejecución
if "pending_tool_call" not in st.session_state:
    st.session_state.pending_tool_call = None

client_ai = genai.Client()
server_params = StdioServerParameters(command=r"D:\dev\agent\.venv\Scripts\python.exe", args=["mcp_server.py"])

async def call_mcp_tool(tool_name: str, tool_args: dict) -> str:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_result = await session.call_tool(tool_name, tool_args)
            return mcp_result.content[0].text

async def get_mcp_tools():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()
            return mcp_tools.tools

@st.cache_resource
def get_gemini_tools():
    mcp_tools = asyncio.run(get_mcp_tools())
    return [{"function_declarations": [
        {"name": t.name, "description": t.description, "parameters": t.inputSchema}
    ]} for t in mcp_tools]

try:
    gemini_tools = get_gemini_tools()
except Exception as e:
    st.error(f"Error inicial al conectar con MCP Server: {e}")
    st.stop()

def render_messages():
    for msg in st.session_state.gemini_messages:
        role = "assistant" if msg.role == "model" else "user"
        with st.chat_message(role):
            for p in msg.parts:
                if hasattr(p, "text") and p.text:
                    st.write(p.text)
                elif hasattr(p, "function_call") and p.function_call:
                    args = dict(p.function_call.args) if hasattr(p.function_call.args, 'items') else str(p.function_call.args)
                    st.info(f"🛠️ **Intención de ejecutar**: `{p.function_call.name}`\n\nArgumentos:\n`{args}`")
                elif hasattr(p, "function_response") and p.function_response:
                    res = p.function_response.response.get("result", "")
                    st.success(f"✅ **Resultado devuelto de `{p.function_response.name}`**:\n```\n{res}\n```")

render_messages()

def safe_generate_content(prompt, config, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client_ai.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=config
            )
        except ClientError as e:
            if e.code == 429:
                st.warning(f"Rate limit alcanzado. Esperando 60 segundos (Intento {attempt + 1}/{max_retries})...")
                time.sleep(60)
            else:
                raise e
    raise Exception("Max retries superados por HTTP 429.")

def run_agent_loop(new_user_text=None):
    if new_user_text:
        # Añadir nuevo mensaje del usuario
        st.session_state.gemini_messages.append(types.Content(role="user", parts=[types.Part.from_text(text=new_user_text)]))
        with st.chat_message("user"):
            st.write(new_user_text)

    with st.spinner("Procesando consulta inicial..." if new_user_text else "Continuando ciclo del agente (Pausa de 4s por rate limit)..."):
        while True:
            # Pausa obligada si venimos de ejecutar una herramienta para evitar 429 Error
            if not new_user_text:
                time.sleep(4)
                
            response = safe_generate_content(
                prompt=st.session_state.gemini_messages,
                config={"tools": gemini_tools, "temperature": 0.0}
            )
            
            # Guardamos respuesta de modelo
            model_content = response.candidates[0].content
            
            # Fix role issue internally if needed
            if not getattr(model_content, 'role', None):
                model_content.role = "model"
                
            st.session_state.gemini_messages.append(model_content)
            
            # Mostramos en UI este nuevo mensaje
            with st.chat_message("assistant"):
                for p in model_content.parts:
                    if hasattr(p, "text") and p.text:
                        st.write(p.text)
                    elif hasattr(p, "function_call") and p.function_call:
                        args = dict(p.function_call.args) if hasattr(p.function_call.args, 'items') else str(p.function_call.args)
                        st.info(f"🛠️ **Solicita ejecutar**: `{p.function_call.name}`\nArgumentos: `{args}`")
            
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call.args, 'items') else dict(call.args)
                st.session_state.pending_tool_call = {"name": call.name, "args": args}
                # Detener la ejecución del agente hasta revisión
                st.rerun()
                return

            # Fin del ciclo: no pidió funciones
            break

# SI HAY HERRAMIENTA PENDIENTE, MOSTRAR PANEL
if st.session_state.pending_tool_call:
    tool_info = st.session_state.pending_tool_call
    st.warning(f"⚠️ El agente necesita ejecutar `{tool_info['name']}` para continuar.\n\nArgumentos:\n`{tool_info['args']}`\n\n¿Autorizas la ejecución en tu sistema?")
    
    col1, col2 = st.columns(2)
    if col1.button("✅ Aprobar Ejecución", use_container_width=True):
        with st.spinner(f"Ejecutando {tool_info['name']} localmente..."):
            try:
                mcp_result = asyncio.run(call_mcp_tool(tool_info['name'], tool_info['args']))
            except Exception as e:
                mcp_result = f"Error ejecutando herramienta: {e}"
            
            # Añadir la respuesta simulando rol 'user' proveyendo function_response
            tool_response_part = types.Part.from_function_response(
                name=tool_info['name'],
                response={"result": str(mcp_result)}
            )
            tool_content = types.Content(role="user", parts=[tool_response_part])
            st.session_state.gemini_messages.append(tool_content)
            
            st.session_state.pending_tool_call = None
            st.rerun()
            
    if col2.button("🚫 Cancelar y Notificar al Agente", use_container_width=True):
        tool_response_part = types.Part.from_function_response(
            name=tool_info['name'],
            response={"result": "Ejecución denegada/cancelada por el usuario."}
        )
        tool_content = types.Content(role="user", parts=[tool_response_part])
        st.session_state.gemini_messages.append(tool_content)
        
        st.session_state.pending_tool_call = None
        st.rerun()

# SI ESTAMOS ESPERANDO INPUT
elif prompt := st.chat_input("Escribe tu instrucción al agente..."):
    run_agent_loop(new_user_text=prompt)
    st.rerun()

# SI DEBEMOS CONTINUAR CICLO AUTOMÁTICAMENTE
else:
    if st.session_state.gemini_messages:
        last_msg = st.session_state.gemini_messages[-1]
        # Continuar si la última acción es una respuesta de herramienta
        is_tool_response = (
            last_msg.role == "user" and 
            any(hasattr(p, "function_response") and p.function_response for p in last_msg.parts)
        )
        if is_tool_response and st.session_state.pending_tool_call is None:
            run_agent_loop()