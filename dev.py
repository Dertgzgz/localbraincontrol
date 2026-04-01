import subprocess
import os
import signal
import sys
import time

def run():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(root_dir, ".venv", "Scripts", "python.exe")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("🚀 Inizializing Antigravity Development Environment...")

    # 0. Asegurar carpeta de logs
    logs_dir = os.path.join(root_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    backend_log = open(os.path.join(logs_dir, "backend.log"), "a", encoding="utf-8")
    frontend_log = open(os.path.join(logs_dir, "frontend.log"), "a", encoding="utf-8")

    # 1. Iniciar Backend (FastAPI)
    print(f"📡 Starting Backend (FastAPI)... Logs: logs/backend.log")
    backend_process = subprocess.Popen(
        [venv_python, "api_server.py"],
        cwd=root_dir,
        stdout=backend_log,
        stderr=backend_log,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # Esperar un poco para que el puerto 8000 se libere/ocupe
    time.sleep(2)

    # 2. Iniciar Frontend (Vite)
    print(f"🎨 Starting Frontend (Vite)... Logs: logs/frontend.log")
    frontend_process = subprocess.Popen(
        ["npm.cmd" if os.name == 'nt' else "npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=frontend_log,
        stderr=frontend_log,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    print("\n✅ All systems online!")
    print("🔗 Backend: http://localhost:8000")
    print("🔗 Frontend: http://localhost:5173")
    print("\nPress Ctrl+C in this terminal to stop all processes.")

    try:
        # Mantener el script vivo mientras los procesos corran
        while True:
            time.sleep(1)
            if backend_process.poll() is not None or frontend_process.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("👋 Environment closed.")
        sys.exit(0)

if __name__ == "__main__":
    run()
