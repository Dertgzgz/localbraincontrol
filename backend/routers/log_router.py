from fastapi import APIRouter, Request, HTTPException, Depends
import os
import json
from ..config import logger
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/logs/frontend")
async def receive_frontend_log(request: Request, current_user: str = Depends(get_current_user)): # Protegida
    try:
        data = await request.json()
        log_entry = data.get("logData", {})
        component = data.get("component", "frontend")

        # Ajustar la ruta para que sea relativa a la raíz del proyecto, no al router
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(project_root, "logs", "frontend.log")
        
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return {"status": "success", "message": "Log received"}
    except Exception as e:
        logger.error(f"Error receiving frontend log: {e}")
        raise HTTPException(status_code=500, detail=str(e))
