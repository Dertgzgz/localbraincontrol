import os
import subprocess
import time
import sys
import psutil

def kill_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Usar net_connections() en lugar de connections()
            for conn in proc.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"🛑 Matando proceso {proc.info['name']} (PID: {proc.info['pid']}) en puerto {port}")
                    proc.send_signal(psutil.signal.SIGTERM)
                    proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            try: proc.kill()
            except: pass

def restart():
    print("🔄 Iniciando Reinicio de Infraestructura Antigravity...")
    
    # 1. Limpiar puertos
    for port in [8000, 5173, 5174]:
        kill_process_on_port(port)
    
    time.sleep(1)
    
    # 2. Lanzar dev.py en segundo plano
    # Usamos detatched process para que sobreviva a la muerte del script actual si fuera necesario
    # Pero aquí simplemente lo lanzamos como un proceso nuevo.
    print("🚀 Levantando servicios...")
    venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    subprocess.Popen(
        [venv_python, "dev.py"],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
        start_new_session=True
    )
    
    print("✅ Reinicio enviado. Los logs estarán en logs/backend.log y logs/frontend.log")

if __name__ == "__main__":
    restart()
