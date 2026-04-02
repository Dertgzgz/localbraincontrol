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

    def search_models(self, query: str, limit: int = 5):
        """Busca modelos en Hugging Face."""
        try:
            logger.info(f"Searching for models with query: {query}, limit: {limit}")
            
            # Primero buscar modelos GGUF
            gguf_models = list(self.api.list_models(
                search=f"{query} gguf",
                limit=limit,
                sort="downloads"
            ))
            
            logger.info(f"Found {len(gguf_models)} GGUF models")
            
            if gguf_models:
                result = [
                    {
                        "id": m.modelId,
                        "name": m.modelId.split("/")[-1],
                        "downloads": m.downloads,
                        "likes": m.likes,
                        "tags": m.tags
                    } for m in gguf_models
                ]
                logger.info(f"Returning {len(result)} GGUF models")
                return result
            
            # Si no hay modelos GGUF, buscar modelos generales
            general_models = list(self.api.list_models(
                search=query,
                limit=limit,
                sort="downloads"
            ))
            
            logger.info(f"Found {len(general_models)} general models")
            
            result = [
                {
                    "id": m.modelId,
                    "name": m.modelId.split("/")[-1],
                    "downloads": m.downloads,
                    "likes": m.likes,
                    "tags": m.tags
                } for m in general_models
            ]
            logger.info(f"Returning {len(result)} general models")
            return result
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
            
            # 3. Registrar en Ollama
            import subprocess
            result = subprocess.run(
                ["ollama", "create", model_name, "-f", modelfile_path],
                capture_output=True,
                text=True,
                cwd=target_dir
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "model": model_name,
                    "file": file_path,
                    "message": f"Model {model_name} created successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to create model: {result.stderr}"
                }
            
        except Exception as e:
            logger.error(f"Error in HF download/register: {e}")
            return {"status": "error", "message": str(e)}

hf_service = HuggingFaceService()
