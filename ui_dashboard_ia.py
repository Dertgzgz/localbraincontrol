import os
import psutil
import streamlit as st
from sys_hardware_monitor import get_gpu_stats, get_ollama_data
from i18n import t

def render_dashboard():
    st.title(t("dash_title"))
    st.markdown(t("dash_subtitle"))
    
    st.header(t("hw_metrics"))
    col1, col2, col3 = st.columns(3)
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    col1.metric(t("cpu_total"), f"{cpu_percent:.1f}%")
    
    ram = psutil.virtual_memory()
    col2.metric(t("ram_sys"), f"{ram.percent:.1f}%", f"{ram.used/1024**3:.1f} / {ram.total/1024**3:.1f} GB")
    
    gpu = get_gpu_stats()
    if gpu:
        col3.metric(t("gpu_nv"), f"{gpu['util']}% Utils", f"{gpu['mem_used']/1024:.1f} GB / {gpu['mem_total']/1024:.1f} GB VRAM")
    else:
        col3.metric("GPU", t("gpu_no"))

    st.divider()
    
    st.header(t("running_models"))
    running_models = get_ollama_data("ps")
    if running_models:
        for m in running_models:
            size_gb = m.get('size', 0) / 1024**3
            vram_gb = m.get('size_vram', 0) / 1024**3
            details = m.get('details', {})
            
            with st.expander(f"🟢 **{m['name']}**", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**{t('family')}**: {details.get('family', 'unknown')}")
                c2.write(f"**{t('params')}**: {details.get('parameter_size', 'unknown')}")
                c3.write(f"**{t('quant')}**: {details.get('quantization_level', 'unknown')}")
                c4.write(f"**{t('total_space')}**: {size_gb:.2f} GB")
                
                st.progress(size_gb / 8.0 if size_gb < 8 else 1.0, text=f"{t('vram_use')} ({vram_gb:.2f} GB reportado en GPU)")
    else:
        st.info(t("no_models"))
        
    st.header(t("avail_images"))
    all_models = get_ollama_data("tags")
    if all_models:
        for m in all_models:
            details = m.get('details', {})
            st.markdown(f"- **{m['name']}** `({details.get('parameter_size', '?')} - {details.get('quantization_level', '?')})`")
    else:
        st.warning(t("no_images"))

    st.divider()

    st.header(t("diag_title"))
    
    col_log, col_model = st.columns(2)
    with col_log:
        log_source = st.selectbox(t("select_log"), ["App Local", "Servidor MCP", "Ollama"])
    with col_model:
        ai_model = st.selectbox(t("select_agent"), ["Antigravity Cloud (Gemini)", "Agente Local (Qwen 3B)"])

    if st.button(t("btn_analyze"), type="primary", use_container_width=True):
        with st.spinner(t("analyzing").format(ai_model)):
            rutas = {
                "App Local": os.path.join(os.path.dirname(__file__), "logs", "app_local.log"),
                "Servidor MCP": os.path.join(os.path.dirname(__file__), "logs", "mcp_server.log"),
                "Ollama": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ollama", "server.log")
            }
            ruta = rutas[log_source]
            
            try:
                with open(ruta, "r", encoding="utf-8", errors="replace") as f:
                    log_data = "".join(f.readlines()[-100:])
            except Exception as e:
                log_data = f"Error leyendo {ruta}: {e}"
            
            if not log_data.strip():
                st.warning(t("log_empty"))
            else:
                prompt_base = t("devops_prompt")
                prompt = (
                    f"{prompt_base}\n"
                    f"--- INICIO DEL LOG ---\n{log_data}\n--- FIN DEL LOG ---"
                )

                try:
                    if "Qwen" in ai_model:
                        from langchain_ollama import ChatOllama
                        from langchain_core.messages import HumanMessage
                        llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0, num_ctx=8192)
                        res = llm.invoke([HumanMessage(content=prompt)])
                        dictamen = res.content
                    else:
                        from google import genai
                        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        dictamen = res.text
                        
                    st.success(f"{t('success_analysis')} {ai_model}")
                    with st.expander(t("ver_log"), expanded=False):
                        st.code(log_data, language="log")
                    
                    st.markdown(t("dictamen_title"))
                    st.info(dictamen)
                    
                except Exception as e:
                    st.error(f"{t('error_analysis')} {type(e).__name__} - {str(e)}")
