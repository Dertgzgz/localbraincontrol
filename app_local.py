import os
import sys
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from ui_dashboard_ia import render_dashboard
from ui_chat_terminal import render_chat
import logging
from i18n import t

LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "app_local.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_PATH, encoding="utf-8")
    ]
)

st.set_page_config(page_title="Centro de Control de IA", layout="wide", page_icon="⚙️")

if "lang" not in st.session_state:
    st.session_state.lang = "es"

def update_lang():
    lang_map = {"🇪🇸 Castellano": "es", "🇬🇧 English": "en", "🟢 Euskera": "eu"}
    st.session_state.lang = lang_map[st.session_state.sel_lang]

lang_opts = ["🇪🇸 Castellano", "🇬🇧 English", "🟢 Euskera"]
curr_idx = 0
if st.session_state.lang == "en": curr_idx = 1
elif st.session_state.lang == "eu": curr_idx = 2

def read_last_lines(path, n=30):
    if not os.path.exists(path): return t("no_logs")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return "".join(f.readlines()[-n:])
    except: return t("error_read_log")

with st.sidebar:
    st.selectbox("🌐 Idioma / Language", lang_opts, index=curr_idx, key="sel_lang", on_change=update_lang)
    st.divider()

view = st.sidebar.radio(t("nav_title"), [t("nav_dashboard"), t("nav_terminal")])

with st.sidebar:
    st.divider()
    st.subheader(t("logs_overview"))
    tabs = st.tabs(["App", "MCP", "Ollama"])
    
    with tabs[0]:
        st.code(read_last_lines(LOG_PATH, 15), language="log")
    with tabs[1]:
        mcp_log = os.path.join(os.path.dirname(__file__), "logs", "mcp_server.log")
        st.code(read_last_lines(mcp_log, 15), language="log")
    with tabs[2]:
        ollama_log = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "server.log")
        st.code(read_last_lines(ollama_log, 15), language="log")
    
    if st.button(t("btn_refresh"), use_container_width=True):
        st.rerun()

if view == t("nav_dashboard"):
    render_dashboard()
else:
    render_chat()