# backend/config.py
import os
import json
import asyncio
import logging
from typing import Dict

# Persistencia de Uso
USAGE_FILE = "config/usage_stats.json"
def load_usage():
    try:
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"tokens_consumed": 0, "requests_count": 0, "last_update": ""}

def save_usage(stats):
    try:
        os.makedirs("config", exist_ok=True)
        stats["last_update"] = str(asyncio.get_event_loop().time())
        with open(USAGE_FILE, "w") as f:
            json.dump(stats, f)
    except (OSError, json.JSONEncodeError):
        pass

def track_usage(tokens: int):
    stats = load_usage()
    stats["tokens_consumed"] += tokens
    stats["requests_count"] += 1
    save_usage(stats)

# Configuración de Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("APIServer")