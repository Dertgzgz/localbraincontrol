import json
import streamlit as st
from langchain_core.messages import HumanMessage
from ai_agent_core import ejecutar_agente_local
from i18n import t

def render_chat():
    st.title(t("chat_title"))
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_tool_call" not in st.session_state:
        st.session_state.pending_tool_call = None

    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.write(msg.content)

    if prompt := st.chat_input(t("chat_placeholder")):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            st.write_stream(ejecutar_agente_local(prompt))
            st.rerun()

    if st.session_state.pending_tool_call:
        tool_call = st.session_state.pending_tool_call
        with st.chat_message("assistant"):
            st.warning(f"{t('confirm_req')} `{tool_call['name']}`")
            st.code(json.dumps(tool_call['args'], indent=2), language="json")
            col1, col2 = st.columns(2)
            if col1.button(t("btn_exec"), use_container_width=True):
                st.session_state.pending_tool_call = None
                st.success(t("action_ok"))
                st.rerun()
            if col2.button(t("btn_cancel"), use_container_width=True):
                st.session_state.pending_tool_call = None
                st.rerun()
