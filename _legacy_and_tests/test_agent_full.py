import asyncio
import logging
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Mocking streamlit before importing app_local
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'pending_tool_call' not in st.session_state:
    st.session_state.pending_tool_call = None

from app_local import ejecutar_agente_local

logging.basicConfig(level=logging.INFO)

def test_full():
    print("--- INICIANDO PRUEBA CON EL NUEVO BUCLE MANUAL ---")
    
    prompt = "¿Quién eres y qué archivos ves en el directorio actual?"
    print(f"Pregunta: {prompt}")
    
    # Simular mensaje del usuario
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    # Ejecutamos el generador
    content = ""
    for chunk in ejecutar_agente_local(prompt):
        content += chunk
    
    print("\n--- RESPUESTA FINAL DEL AGENTE ---")
    print(content)
    
    if "OpenAI" in content:
        print("❌ FALLO: Sigue atrapado en la identidad de OpenAI.")
    elif "listar_directorio" in content.lower() or "mcp_server.py" in content.lower():
        print("✅ ÉXITO: El agente usó herramientas o reportó contenido real.")
    else:
        print("⚠️ RESULTADO NEUTRAL: Respondió algo pero no está claro si usó herramientas.")

if __name__ == "__main__":
    test_full()
