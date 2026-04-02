#!/usr/bin/env python3
"""
Error Analyzer - Sistema de logging unificado para errores de backend y frontend
"""

import os
import re
import time
import logging
from datetime import datetime
from pathlib import Path

class UnifiedErrorLogger:
    def __init__(self, logs_dir="logs"):
        self.logs_dir = Path(logs_dir)
        self.backend_log = self.logs_dir / "backend.log"
        self.frontend_log = self.logs_dir / "frontend.log"
        self.unified_log = self.logs_dir / "unified_errors.log"

        # Configurar logging unificado
        self.logger = logging.getLogger("UnifiedErrorLogger")
        self.logger.setLevel(logging.ERROR)

        # Handler para archivo unificado
        handler = logging.FileHandler(self.unified_log, encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(component)s - %(message)s'
        ))
        self.logger.addHandler(handler)

        # Patrones de error más específicos
        self.error_patterns = {
            'backend': [
                r'ERROR:.*Exception:.*',
                r'ERROR:.*Error.*',
                r'ERROR:.*Failed.*',
                r'ERROR:.*Traceback.*',
                r'Exception:.*',
                r'Traceback.*',
                r'Error in.*',
                r'404 Client Error.*'
            ],
            'frontend': [
                r'ERROR.*',
                r'Error:.*',
                r'Uncaught.*',
                r'Exception.*',
                r'ReferenceError.*',
                r'TypeError.*',
                r'SyntaxError.*'
            ]
        }

    def extract_errors_from_file(self, file_path, component):
        """Extrae errores de un archivo de log"""
        if not file_path.exists():
            return []

        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    # Solo procesar líneas que realmente son errores
                    is_error = False
                    for pattern in self.error_patterns[component]:
                        if re.search(pattern, line, re.IGNORECASE):
                            is_error = True
                            break
                    
                    if is_error:
                        errors.append({
                            'line': line_num,
                            'content': line,
                            'timestamp': datetime.now().isoformat(),
                            'component': component
                        })
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}", extra={'component': 'analyzer'})

        return errors

    def analyze_and_log(self):
        """Analiza logs y registra errores unificados"""
        print("🔍 Analizando logs de errores...")

        backend_errors = self.extract_errors_from_file(self.backend_log, 'backend')
        frontend_errors = self.extract_errors_from_file(self.frontend_log, 'frontend')

        all_errors = backend_errors + frontend_errors

        if all_errors:
            print(f"🚨 Encontrados {len(all_errors)} errores:")
            for error in all_errors:
                print(f"  [{error['component'].upper()}] {error['content']}")

                # Log unificado
                self.logger.error(
                    error['content'],
                    extra={
                        'component': error['component'],
                        'line': error['line']
                    }
                )
        else:
            print("✅ No se encontraron errores en los logs")

        return all_errors

    def monitor_logs(self, interval=30):
        """Monitorea logs en tiempo real"""
        print(f"👀 Monitoreando logs cada {interval} segundos...")
        print("Presiona Ctrl+C para detener")

        last_backend_size = 0
        last_frontend_size = 0

        try:
            while True:
                # Verificar cambios en archivos
                backend_size = self.backend_log.stat().st_size if self.backend_log.exists() else 0
                frontend_size = self.frontend_log.stat().st_size if self.frontend_log.exists() else 0

                if backend_size > last_backend_size or frontend_size > last_frontend_size:
                    errors = self.analyze_and_log()
                    if errors:
                        print(f"📝 Registrados {len(errors)} nuevos errores en log unificado")

                last_backend_size = backend_size
                last_frontend_size = frontend_size

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n🛑 Monitoreo detenido")

def main():
    analyzer = UnifiedErrorLogger()

    print("=== UNIFIED ERROR LOGGER ===")
    print(f"Backend log: {analyzer.backend_log}")
    print(f"Frontend log: {analyzer.frontend_log}")
    print(f"Unified log: {analyzer.unified_log}")
    print()

    # Análisis inicial
    analyzer.analyze_and_log()
    print()

    # Monitoreo continuo
    analyzer.monitor_logs()

if __name__ == "__main__":
    main()