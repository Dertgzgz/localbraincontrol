import streamlit as st

TRANSLATIONS = {
    # Navegación y UI Base (app_local.py)
    "nav_title": {"es": "Navegación", "en": "Navigation", "eu": "Nabigazioa"},
    "nav_dashboard": {"es": "Panel de Control", "en": "Dashboard", "eu": "Kontrol Panela"},
    "nav_terminal": {"es": "Terminal de Agente", "en": "Agent Terminal", "eu": "Agentearen Terminala"},
    "logs_overview": {"es": "Vistazo de Logs", "en": "Logs Overview", "eu": "Log-en Ikuspegia"},
    "no_logs": {"es": "No hay logs disponibles.", "en": "No logs available.", "eu": "Ez dago logik erabilgarri."},
    "error_read_log": {"es": "Error leyendo log.", "en": "Error reading log.", "eu": "Errorea loga irakurtzean."},
    "btn_refresh": {"es": "Refrescar", "en": "Refresh", "eu": "Freskatu"},
    "nav_models": {"es": "Gestor de Modelos", "en": "Model Manager", "eu": "Muduen Kudeatzailea"},
    "nav_settings": {"es": "Ajustes", "en": "Settings", "eu": "Ezarpenak"},
    "usage_title": {"es": "Cuotas de Uso", "en": "Usage Quotas", "eu": "Erabilera Kuotak"},
    "usage_tokens": {"es": "Tokens Consumidos", "en": "Tokens Consumed", "eu": "Kontsumitutako Tokenak"},
    "usage_requests": {"es": "Peticiones Realizadas", "en": "Requests Made", "eu": "Egindako Eskaerak"},
    "model_selector_title": {"es": "Modelo IA", "en": "AI Model", "eu": "IA Eredua"},
    
    # Dashboard (ui_dashboard_ia.py)
    "dash_title": {"es": "Centro de Control IA (Dashboard)", "en": "AI Control Center (Dashboard)", "eu": "IA Kontrol Zentroa (Dashboard)"},
    "dash_subtitle": {"es": "Gestión de Infraestructura de Inteligencia Artificial Local", "en": "Local Artificial Intelligence Infrastructure Management", "eu": "Adimen Artifizial Lokaleko Azpiegituraren Kudeaketa"},
    "hw_metrics": {"es": "Hardware Metrics", "en": "Hardware Metrics", "eu": "Hardware Metrikak"},
    "cpu_total": {"es": "CPU Total", "en": "Total CPU", "eu": "CPU Guztira"},
    "ram_sys": {"es": "RAM del Sistema", "en": "System RAM", "eu": "Sistemaren RAMa"},
    "gpu_nv": {"es": "GPU NVIDIA", "en": "NVIDIA GPU", "eu": "NVIDIA GPUa"},
    "gpu_no": {"es": "No disponible", "en": "Not available", "eu": "Ez dago erabilgarri"},
    "running_models": {"es": "Modelos en Ejecución (RAM/VRAM)", "en": "Running Models (RAM/VRAM)", "eu": "Exekuzioan dauden Ereduak (RAM/VRAM)"},
    "family": {"es": "Familia", "en": "Family", "eu": "Familia"},
    "params": {"es": "Parámetros", "en": "Parameters", "eu": "Parametroak"},
    "quant": {"es": "Cuantización", "en": "Quantization", "eu": "Kuantizazioa"},
    "total_space": {"es": "Espacio Total", "en": "Total Space", "eu": "Espazio Guztira"},
    "vram_use": {"es": "Consumo de VRAM", "en": "VRAM Usage", "eu": "VRAMaren Kontsumoa"},
    "no_models": {"es": "No hay modelos cargados en memoria. El servidor Ollama está inactivo o a la espera.", "en": "No models loaded into memory. The Ollama server is inactive or waiting.", "eu": "Ez dago eredurik memoriara kargatuta. Ollama zerbitzaria inaktibo edo zain dago."},
    "avail_images": {"es": "Imágenes Disponibles (Ollama)", "en": "Available Images (Ollama)", "eu": "Irudi Erabilgarriak (Ollama)"},
    "no_images": {"es": "No se pudieron cargar las imágenes de Ollama.", "en": "Could not load Ollama images.", "eu": "Ezin izan dira Ollama irudiak kargatu."},
    
    # Model Manager
    "cat_general": {"es": "General Chat", "en": "General Chat", "eu": "Txat Orokorra"},
    "cat_coding": {"es": "Programación", "en": "Coding", "eu": "Programazioa"},
    "cat_vision": {"es": "Visión", "en": "Vision", "eu": "Ikusmena"},
    "cat_small": {"es": "Ligeros / Edge", "en": "Small / Edge", "eu": "Arinak / Edge"},
    "pull_model": {"es": "Descargar Modelo", "en": "Pull Model", "eu": "Eredua Deskargatu"},
    "pulling": {"es": "Descargando...", "en": "Downloading...", "eu": "Deskargatzen..."},
    "delete_model": {"es": "Eliminar del disco", "en": "Delete from disk", "eu": "Diskotik ezabatu"},
    "confirm_delete": {"es": "¿Confirmar eliminación?", "en": "Confirm deletion?", "eu": "Ezabatzea berretsi?"},
    "model_search": {"es": "Buscar en Ollama Library...", "en": "Search Ollama Library...", "eu": "Ollama Liburutegian bilatu..."},
    
    # Análisis Logs
    "diag_title": {"es": "Diagnóstico Inteligente de Logs", "en": "Intelligent Log Diagnostics", "eu": "Log-en Diagnostiko Adimenduna"},
    "select_log": {"es": "Selecciona el Log a analizar", "en": "Select Log to analyze", "eu": "Hautatu aztertzeko Log-a"},
    "select_agent": {"es": "Selecciona el Agente Analista", "en": "Select Analyst Agent", "eu": "Hautatu Agente Analista"},
    "btn_analyze": {"es": "Analizar y Emitir Dictamen", "en": "Analyze and Issue Opinion", "eu": "Aztertu eta Iritzia Eman"},
    "analyzing": {"es": "Analizando registros usando {}...", "en": "Analyzing records using {}...", "eu": "Erregistroak aztertzen {} erabiliz..."},
    "log_empty": {"es": "El log seleccionado está vacío o no contiene información relevante.", "en": "The selected log is empty or contains no relevant information.", "eu": "Hautatutako log-a hutsik dago edo ez dauka informazio garrantzitsurik."},
    "success_analysis": {"es": "Análisis completado por", "en": "Analysis completed by", "eu": "Azterketa osatuta ("},
    "ver_log": {"es": "📄 Ver Log Extraído (Contexto)", "en": "📄 View Extracted Log (Context)", "eu": "📄 Ikusi Erauzitako Log-a (Testuingurua)"},
    "dictamen_title": {"es": "### 📋 Dictamen de Diagnóstico", "en": "### 📋 Diagnostic Opinion", "eu": "### 📋 Diagnostikoaren Iritzia"},
    "error_analysis": {"es": "Error generando dictamen con el modelo:", "en": "Error generating opinion with model:", "eu": "Errorea ereduarekin iritzia sortzerakoan:"},
    "sys_instructions": {"es": "Instrucciones del Sistema (Prompt)", "en": "System Instructions (Prompt)", "eu": "Sistemaren Argibideak (Prompt)"},
    "log_peek": {"es": "Vista Previa del Flujo de Datos", "en": "Data Flow Preview", "eu": "Datuen Fluxuaren Aurrebista"},
    "neural_context": {"es": "Contexto Neuronal Activo", "en": "Active Neural Context", "eu": "Testuinguru Neuronal Aktiboa"},
    "source_backend": {"es": "Servidor Backend (FastAPI)", "en": "Backend Server (FastAPI)", "eu": "Backend Zerbitzaria (FastAPI)"},
    "source_frontend": {"es": "Interfaz de Usuario (Vite)", "en": "User Interface (Vite)", "eu": "Erabiltzaile Interfazea (Vite)"},
    "self_healing": {"es": "Modo Auto-Reparación Activo", "en": "Self-Healing Mode Active", "eu": "Auto-konponketa Modua Aktibatuta"},
    
    # Chat Terminal
    "chat_title": {"es": "Agente MCP Local (Optimizado para GPU)", "en": "Local MCP Agent (GPU Optimized)", "eu": "MCP Agente Lokala (GPU Optimizatua)"},
    "chat_placeholder": {"es": "Dime qué hacer...", "en": "Tell me what to do...", "eu": "Esan zer egin..."},
    "confirm_req": {"es": "⚠️ **Confirmación Requerida**:", "en": "⚠️ **Confirmation Required**:", "eu": "⚠️ **Baieztapena Behar Da**:"},
    "btn_exec": {"es": "✅ Ejecutar", "en": "✅ Execute", "eu": "✅ Exekutatu"},
    "btn_cancel": {"es": "❌ Cancelar", "en": "❌ Cancel", "eu": "❌ Utzi"},
    "action_ok": {"es": "Acción aprobada. (Habilitando ejecución en siguiente turno...)", "en": "Action approved. (Enabling execution next turn...)", "eu": "Ekintza onartuta. (Aldaketa baimentzen hurrengo txandan...)"},
    "chat_history": {"es": "Historial de Conversaciones", "en": "Conversation History", "eu": "Berriketen Historiala"},
    "active_context": {"es": "Contexto Activo (Recursos)", "en": "Active Context (Resources)", "eu": "Testuinguru Aktiboa (Baliabideak)"},
    "add_context": {"es": "Añadir Ruta o URL...", "en": "Add Path or URL...", "eu": "Gehitu Bidea edo URLa..."},
    "no_history": {"es": "No hay chats previos.", "en": "No previous chats.", "eu": "Ez dago aldez aurreko txatik."},
    "new_chat": {"es": "Nueva Conversación", "en": "New Conversation", "eu": "Elkarrizketa Berria"},
    "clear_context": {"es": "Limpiar Contexto", "en": "Clear Context", "eu": "Garbitu Testuingurua"},
    "nav_perf": {"es": "Optimización IA", "en": "AI Optimization", "eu": "IA Optimizazioa"},
    "perf_title": {"es": "Centro de Rendimiento y Tuning AI", "en": "AI Performance & Tuning center", "eu": "IA Errendimendu eta Afinazio Zentroa"},
    "ctx_window": {"es": "Ventana de Contexto (Tokens)", "en": "Context Window (Tokens)", "eu": "Testuinguru Leihoa (Tokenak)"},
    "gpu_layers": {"es": "Capas en GPU (VRAM)", "en": "GPU Layers (VRAM)", "eu": "GPU Geruzak (VRAM)"},
    "temperature": {"es": "Creatividad (Temperatura)", "en": "Creativity (Temperature)", "eu": "Sormena (Tenperatura)"},
    "btn_ai_optimize": {"es": "Optimizar con IA Asistida", "en": "Optimize with Assisted AI", "eu": "IA Lagunduarekin Optimizatu"},
    "recommending": {"es": "Analizando hardware para optimizar...", "en": "Analyzing hardware to optimize...", "eu": "Hardwarea aztertzen optimizatzeko..."},
    "apply_changes": {"es": "Aplicar Configuración", "en": "Apply Settings", "eu": "Ezarpenak Aplikatu"},

    # Core (Proceso e IA)
    "sys_lang": {"es": "IDIOMA: Responde siempre en español.", "en": "LANGUAGE: Always answer in English.", "eu": "HIZKUNTZA: Euskaraz erantzun beti."},
    "devops_prompt": {
        "es": "Actúa como un experto en soporte de software (DevOps/SRE) nivel Senior.\nAnaliza estrictamente las siguientes líneas de log e identifica:\n1. Posibles errores críticos (CRITICAL/ERROR/FATAL).\n2. Comportamiento inusual o cuellos de botella.\n3. Una conclusión breve sobre la salud del proceso.\nNo inventes datos, cíñete a las líneas. Si no hay errores, infórmalo.\n\n",
        "en": "Act as a Senior Software Support Expert (DevOps/SRE).\nStrictly analyze the following log lines and identify:\n1. Possible critical errors (CRITICAL/ERROR/FATAL).\n2. Unusual behavior or bottlenecks.\n3. A brief conclusion about the health of the process.\nDo not invent data, stick to the lines. If there are no errors, explicitly state it.\n\n",
        "eu": "Software-euskarriko (DevOps/SRE) aditu senior bezala jokatu.\nModu zorrotzean analizatu log-eko lerro hauek eta identifikatu:\n1. Balizko errore kritikoak (CRITICAL/ERROR/FATAL).\n2. Ezohiko portaera edo inbutu-lepoak.\n3. Prozesuaren osasunari buruzko ondorio labur bat.\nEz asmatu daturik, mugatu lerroetara. Errorerik ez badago, adierazi.\n\n"
    }
}

def t(key: str) -> str:
    """Devuelve la traducción para la key proporcionada basándose en st.session_state.lang"""
    lang = st.session_state.get("lang", "es")
    
    if key not in TRANSLATIONS:
        return key

    return TRANSLATIONS[key].get(lang, TRANSLATIONS[key]["es"])
