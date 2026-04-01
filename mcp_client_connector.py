import sys
import logging
import streamlit as st
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger("AgenteLocal")

@st.cache_resource
def get_mcp_client():
    """
    Inicializa de forma persistente (cacheada en Streamlit) el cliente MCP.
    Conecta este entorno Streamlit directamente con los servidores definidos.
    """
    logger.info("🔌 Iniciando cliente MCP persistente...")
    client = MultiServerMCPClient(
        {
            "recursos_windows": {
                "command": sys.executable,
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    return client
