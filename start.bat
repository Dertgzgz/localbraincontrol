@echo off
echo 🚀 Iniciando Entorno Antigravity...
start "Backend API" .venv/Scripts/python.exe api_server.py
timeout /t 5 /nobreak
start "Frontend React" cmd /c "cd frontend && npm run dev"
echo ✅ Servicios lanzados. Backend: 8000, Frontend: 5173
pause
