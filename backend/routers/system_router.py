# backend/routers/system_router.py
from fastapi import APIRouter, HTTPException
import psutil
import sys
from ..models.schemas import HardwareMetrics
from ..config import logger
from sys_hardware_monitor import get_gpu_stats

router = APIRouter()

@router.get("/system/metrics", response_model=HardwareMetrics)
async def get_system_metrics():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        gpu = get_gpu_stats()
        return {
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "ram_used_gb": ram.used / 1024**3,
            "ram_total_gb": ram.total / 1024**3,
            "gpu": gpu
        }
    except Exception as e:
        logger.error(f"Error en metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/usage")
async def get_usage_stats():
    from ..config import load_usage
    return load_usage()

@router.get("/system/capabilities")
async def get_system_capabilities():
    mem = psutil.virtual_memory()
    return {"os": sys.platform, "cpu_threads": psutil.cpu_count(), "ram_total_gb": round(mem.total / (1024**3), 2)}