import os
import httpx
import json
import logging
import asyncio
from modelscope import HubApi

logger = logging.getLogger(__name__)

class ModelScopeService:
    def __init__(self):
        self.api = HubApi()

    def search_models(self, query: str, limit: int = 5):
        """Busca modelos en ModelScope."""
        try:
            models = self.api.search_models(
                query=query,
                limit=limit,
                sort_by="downloads",
                sort_direction="desc"
            )
            return [
                {
                    "id": m.model_id,
                    "name": m.model_id.split("/")[-1],
                    "downloads": m.downloads,
                    "likes": m.likes or 0,
                    "tags": m.tags or [],
                    "description": m.description or ""
                } for m in models
            ]
        except Exception as e:
            logger.error(f"Error searching ModelScope: {e}")
            return []

    def download_and_register(self, model_id: str, target_dir: str):
        """Descarga un modelo de ModelScope."""
        os.makedirs(target_dir, exist_ok=True)
        
        try:
            # ModelScope tiene su propia API de descarga
            from modelscope import snapshot_download
            model_path = snapshot_download(model_id, cache_dir=target_dir)
            
            return {
                "status": "success",
                "model": model_id.split("/")[-1],
                "path": model_path,
                "message": f"Model downloaded to {model_path}"
            }
        except Exception as e:
            logger.error(f"Error downloading from ModelScope: {e}")
            return {"status": "error", "message": str(e)}

modelscope_service = ModelScopeService()