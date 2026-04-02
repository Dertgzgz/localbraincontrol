# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.auth_router import router as auth_router
from .routers.system_router import router as system_router
from .routers.agent_router import router as agent_router
from .routers.config_router import router as config_router
from .routers.log_router import router as log_router
# Agregar más routers aquí

app = FastAPI(title="Antigravity Local AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(log_router, prefix="/api")
# Agregar más includes aquí