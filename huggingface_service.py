import os
import httpx
import json
import logging
import asyncio
from huggingface_hub import hf_hub_download, HfApi

logger = logging.getLogger(__name__)

class HuggingFaceService:
    def __init__(self):
        self.api = HfApi()

    async def search_models(self, query: str, limit: int = 5):
        """Busca modelos en Hugging Face que tengan formato GGUF."""
        try:
            models = self.api.list_models(
                search=query,
                tags="gguf",
                limit=limit,
                sort="downloads",
                direction=-1
            )
            return [
                {
                    "id": m.modelId,
                    "name": m.modelId.split("/")[-1],
                    "downloads": m.downloads,
                    "likes": m.likes,
                    "tags": m.tags
                } for m in models
            ]
        except Exception as e:
            logger.error(f"Error searching HF: {e}")
            return []

    def download_and_register(self, repo_id: str, filename: str, target_dir: str):
        """Descarga un GGUF y crea un modelo de Ollama asociado."""
        os.makedirs(target_dir, exist_ok=True)
        
        try:
            # 1. Descargar el archivo
            file_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=target_dir
            )
            
            # 2. Crear Modelfile
            model_name = filename.split(".")[0].lower()
            modelfile_content = f"FROM {file_path}"
            modelfile_path = os.path.join(target_dir, f"Modelfile_{model_name}")
            
            with open(modelfile_path, "w") as f:
                f.write(modelfile_content)
            
            # 3. Registrar en Ollama (Vía CLI por simplicidad de streaming si fuera necesario, 
            # pero aquí usamos una petición HTTP simple)
            return {
                "status": "success",
                "model": model_name,
                "file": file_path,
                "command": f"ollama create {model_name} -f {modelfile_path}"
            }
            
        except Exception as e:
            logger.error(f"Error in HF download/register: {e}")
            return {"status": "error", "message": str(e)}

hf_service = HuggingFaceService()
