import subprocess
import requests
import logging

logger = logging.getLogger("AgenteLocal")

def get_gpu_stats():
    """
    Lee las métricas de la GPU utilizando nvidia-smi.
    Devuelve diccionario con 'util' (porcentaje), 'mem_used' (MB) y 'mem_total' (MB).
    """
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        )
        parts = output.strip().split(",")
        if len(parts) == 3:
            return {
                "util": float(parts[0]),
                "mem_used": float(parts[1]),
                "mem_total": float(parts[2])
            }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas nvidia-smi: {e}")
        return None

def get_ollama_data(endpoint):
    """
    Se conecta a la API local de Ollama (http://localhost:11434) y obtiene 'tags' o 'ps'.
    """
    try:
        r = requests.get(f"http://localhost:11434/api/{endpoint}", timeout=2)
        if r.status_code == 200:
            return r.json().get("models", [])
    except Exception as e:
        logger.error(f"Error consultando Ollama API ({endpoint}): {e}")
    return []
