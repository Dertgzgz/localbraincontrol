# Sistema de Logging Unificado de Errores

## Descripción
Este sistema combina errores del backend (Python/FastAPI) y frontend (React/Vite) en un log unificado para análisis holístico.

## Componentes

### 1. Backend (api_server.py)
- **Endpoint**: `POST /api/errors/log`
- Registra errores enviados desde el frontend
- Mantiene logging estándar de Python

### 2. Frontend (main.jsx)
- **Event Listeners**:
  - `error`: Captura errores de JavaScript no manejados
  - `unhandledrejection`: Captura promesas rechazadas
- Envía errores automáticamente al backend

### 3. Analizador Unificado (error_analyzer.py)
- **Función**: Analiza logs existentes y extrae errores
- **Modos**:
  - Análisis único: `python error_analyzer.py` (termina después de analizar)
  - Monitoreo continuo: `python error_analyzer.py` (corre indefinidamente)

## Archivos de Log

- `logs/backend.log`: Errores del backend
- `logs/frontend.log`: Errores del frontend (limitado)
- `logs/unified_errors.log`: Errores combinados y analizados

## Uso

### Análisis Manual
```bash
cd /path/to/project
python error_analyzer.py
```

### Monitoreo Continuo
```bash
python error_analyzer.py  # Se ejecuta indefinidamente
# Presiona Ctrl+C para detener
```

### Ver Log Unificado
```bash
tail -f logs/unified_errors.log
```

## Formato de Errores

Cada error en el log unificado incluye:
- Timestamp
- Nivel (ERROR)
- Componente (backend/frontend/analyzer)
- Mensaje de error
- Stack trace (si disponible)
- Metadatos adicionales (línea, URL, etc.)

## Beneficios

1. **Análisis Holístico**: Ver todos los errores del sistema en un lugar
2. **Trazabilidad**: Correlacionar errores entre frontend y backend
3. **Monitoreo en Tiempo Real**: Detección automática de nuevos errores
4. **Debugging Mejorado**: Contexto completo para resolución de problemas

## Próximos Pasos

- Agregar alertas por email/Slack para errores críticos
- Dashboard web para visualizar errores
- Filtros y búsqueda avanzada
- Métricas de errores por componente