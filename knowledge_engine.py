import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("KnowledgeEngine")
logger.setLevel(logging.DEBUG)

KNOWLEDGE_DIR = "config/knowledge"
KNOWLEDGE_FILE = os.path.join(KNOWLEDGE_DIR, "system_memory.json")

def get_knowledge_summary():
    """Retorna un resumen estructurado de la base de conocimientos para inyectar en el prompt."""
    try:
        if not os.path.exists(KNOWLEDGE_FILE):
            return "No hay conocimientos previos registrados."
        
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        summary = "# BASE DE CONOCIMIENTOS EVOLUTIVA\n"
        for category, items in data.items():
            summary += f"\n## {category.upper()}\n"
            for item in items:
                summary += f"- {item['content']} (Registrado: {item['timestamp']})\n"
        return summary
    except Exception as e:
        logger.error(f"Error leyendo base de conocimientos: {e}")
        return "Error cargando conocimientos."

def update_knowledge(category: str, content: str):
    """Añade o actualiza una entrada en la base de conocimientos."""
    try:
        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
        
        data = {}
        if os.path.exists(KNOWLEDGE_FILE):
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        if category not in data:
            data[category] = []
            
        data[category].append({
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limitar a las últimas 20 entradas por categoría para evitar saturación
        data[category] = data[category][-20:]
        
        with open(KNOWLEDGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Conocimiento actualizado: [{category}] {content[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Error actualizando base de conocimientos: {e}")
        return False
