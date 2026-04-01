import asyncio
import os
import subprocess
import logging
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult
from playwright.async_api import async_playwright
from knowledge_engine import update_knowledge

# Configuración de logs en archivo (evitando stdout para no romper el protocolo MCP)
LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "mcp_server.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger = logging.getLogger("mcp_server")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Inicializar servidor
app = Server("windows-fs-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Expone las herramientas disponibles al cliente."""
    return [
        Tool(
            name="leer_logs",
            description="Lee las últimas líneas de un log (ollama, app, server, mcp).",
            inputSchema={
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "enum": ["ollama", "app", "mcp"], "description": "Tipo de log a leer."},
                    "lineas": {"type": "integer", "default": 50, "description": "Número de líneas desde el final."}
                },
                "required": ["tipo"]
            }
        ),
        Tool(
            name="listar_directorio",
            description="Lista archivos y carpetas en una ruta local de Windows",
            inputSchema={
                "type": "object",
                "properties": {"ruta": {"type": "string", "description": "Ruta absoluta, ej: C:\\"}},
                "required": ["ruta"]
            }
        ),
        Tool(
            name="escribir_archivo",
            description="Escribe contenido de texto en un archivo local.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string", "description": "Ruta absoluta del archivo destino."},
                    "contenido": {"type": "string", "description": "Contenido a escribir en el archivo."}
                },
                "required": ["ruta", "contenido"]
            }
        ),
        Tool(
            name="ejecutar_comando",
            description="Ejecuta un comando en la terminal local del sistema (CMD/PowerShell) y retorna la salida.",
            inputSchema={
                "type": "object",
                "properties": {
                    "comando": {"type": "string", "description": "El comando a ejecutar."}
                },
                "required": ["comando"]
            }
        ),
        Tool(
            name="interactuar_navegador",
            description="Abre una URL en el navegador y permite leer contenido, hacer click o escribir texto.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL completa a visitar."},
                    "accion": {"type": "string", "enum": ["leer", "click", "escribir"], "description": "Acción a realizar en la página."},
                    "selector": {"type": "string", "description": "Selector CSS del elemento objetivo (opcional si la acción es leer todo el body)."},
                    "texto": {"type": "string", "description": "Texto a introducir si la acción es 'escribir'."}
                },
                "required": ["url", "accion"]
            }
        ),
        Tool(
            name="leer_archivo",
            description="Lee el contenido de texto de un archivo local.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string", "description": "Ruta absoluta del archivo a leer."}
                },
                "required": ["ruta"]
            }
        ),
        Tool(
            name="eliminar_archivo",
            description="Elimina un archivo del sistema local. Herramienta PERSISTENTE y PELIGROSA.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ruta": {"type": "string", "description": "Ruta absoluta del archivo a eliminar."}
                },
                "required": ["ruta"]
            }
        ),
        Tool(
            name="obtener_info_sistema",
            description="Obtiene información detallada sobre el sistema operativo, CPU y memoria.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="consultar_agente_local",
            description="Envía un prompt de razonamiento o pregunta al modelo de IA local (Qwen 3B). Usa esta herramienta para delegar generación de código, analíticas pesadas o redacción creativa sin bloquear tu propio hilo de razonamiento.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "La instrucción, pregunta o código que el agente local debe analizar."}
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="actualizar_conocimiento",
            description="Guarda un aprendizaje o dato clave en la base de conocimientos persistente del sistema.",
            inputSchema={
                "type": "object",
                "properties": {
                    "categoria": {"type": "string", "description": "Categoría (ej: hardware, logs, proyecto, preferencias)"},
                    "contenido": {"type": "string", "description": "El dato o aprendizaje a recordar."}
                },
                "required": ["categoria", "contenido"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Ejecuta la herramienta solicitada."""
    
    if name == "actualizar_conocimiento":
        cat = arguments.get("categoria")
        cont = arguments.get("contenido")
        success = update_knowledge(cat, cont)
        return CallToolResult(content=[TextContent(type="text", text="✅ Conocimiento guardado." if success else "❌ Error al guardar.")])

    elif name == "consultar_agente_local":
        prompt = arguments.get("prompt")
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import HumanMessage
            llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0, num_ctx=8192)
            mensajes = [HumanMessage(content=prompt)]
            logger.info(f"🧠 Derivando query a Qwen 3B: '{prompt[:50]}...'")
            respuesta = await llm.ainvoke(mensajes)
            return CallToolResult(content=[TextContent(type="text", text=respuesta.content)])
        except Exception as e:
            logger.error(f"Error Qwen 3B Local: {str(e)}")
            return CallToolResult(content=[TextContent(type="text", text=f"Fallo del motor esclavo local: {str(e)}")])

    elif name == "leer_logs":
        tipo = arguments.get("tipo")
        n_lineas = arguments.get("lineas", 50)
        rutas = {
            "ollama": os.path.join(os.environ["LOCALAPPDATA"], "Ollama", "server.log"),
            "app": os.path.join(os.path.dirname(__file__), "logs", "app_local.log"),
            "mcp": os.path.join(os.path.dirname(__file__), "logs", "mcp_server.log")
        }
        ruta = rutas.get(tipo)
        if not ruta or not os.path.exists(ruta):
            return CallToolResult(content=[TextContent(type="text", text=f"Log {tipo} no encontrado en {ruta}")])
        try:
            with open(ruta, "r", encoding="utf-8", errors="replace") as f:
                lineas = f.readlines()
                ultimas = "".join(lineas[-n_lineas:])
                return CallToolResult(content=[TextContent(type="text", text=f"--- Mostrando últimas {n_lineas} líneas de {tipo} ---\n{ultimas}")])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error leyendo log: {str(e)}")])

    elif name == "listar_directorio":
        ruta = arguments.get("ruta", ".")
        try:
            archivos = "\n".join(os.listdir(ruta))
            return CallToolResult(content=[TextContent(type="text", text=archivos if archivos else "Directorio vacío.")])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])
            
    elif name == "escribir_archivo":
        ruta = arguments.get("ruta")
        contenido = arguments.get("contenido", "")
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            return CallToolResult(content=[TextContent(type="text", text=f"Archivo escrito exitosamente en {ruta}")])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error al escribir archivo: {str(e)}")])

    elif name == "leer_archivo":
        ruta = arguments.get("ruta")
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            return CallToolResult(content=[TextContent(type="text", text=contenido)])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error al leer archivo: {str(e)}")])

    elif name == "eliminar_archivo":
        ruta = arguments.get("ruta")
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
                return CallToolResult(content=[TextContent(type="text", text=f"Archivo {ruta} eliminado exitosamente.")])
            else:
                return CallToolResult(content=[TextContent(type="text", text=f"El archivo {ruta} no existe.")])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error al eliminar archivo: {str(e)}")])

    elif name == "obtener_info_sistema":
        try:
            proceso = subprocess.run(
                ['powershell', '-Command', 'Get-ComputerInfo | Select-Object OSName, OsVersion, WindowsVersion, CsName, CsProcessors, CsTotalPhysicalMemory | Out-String'],
                capture_output=True, text=True, errors="replace"
            )
            return CallToolResult(content=[TextContent(type="text", text=proceso.stdout)])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error al obtener info sistema: {str(e)}")])

    elif name == "ejecutar_comando":
        comando = arguments.get("comando")
        try:
            proceso = subprocess.run(
                comando, shell=True, capture_output=True, text=True, errors="replace"
            )
            salida = proceso.stdout
            if proceso.stderr:
                salida += f"\n[ERRORES/STDERR]:\n{proceso.stderr}"
            if not salida.strip():
                salida = "Comando ejecutado exitosamente sin salida."
            return CallToolResult(content=[TextContent(type="text", text=salida)])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error al ejecutar comando: {str(e)}")])

    elif name == "interactuar_navegador":
        url = arguments.get("url")
        accion = arguments.get("accion")
        selector = arguments.get("selector")
        texto = arguments.get("texto", "")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False) 
                page = await browser.new_page()
                await page.goto(url, wait_until="domcontentloaded")
                resultado = ""
                if accion == "leer":
                    resultado = await page.locator(selector or "body").inner_text()
                elif accion == "click":
                    if not selector: raise ValueError("Se requiere un 'selector' para hacer click.")
                    await page.click(selector)
                    await page.wait_for_timeout(1000)
                    resultado = f"Click ejecutado exitosamente en {selector}."
                elif accion == "escribir":
                    if not selector: raise ValueError("Se requiere un 'selector' para escribir.")
                    await page.fill(selector, texto)
                    resultado = f"Texto '{texto}' introducido en {selector}."
                await browser.close()
                return CallToolResult(content=[TextContent(type="text", text=resultado or "Acción completada sin retorno de texto.")])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text", text=f"Error de Playwright: {str(e)}")])

    raise ValueError(f"Herramienta no encontrada: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())