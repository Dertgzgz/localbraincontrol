

# LocalBrainControl

**LocalBrainControl** es una solución robusta para la orquestación y el control de modelos de lenguaje de gran tamaño (LLMs) ejecutados localmente. El proyecto se centra en la privacidad, la baja latencia y la independencia de servicios en la nube, permitiendo integrar capacidades de IA directamente en flujos de trabajo locales.



## 🚀 Características Principales

* **Inferencia Privada:** Todo el procesamiento ocurre en tu hardware. Sin telemetría externa.
* **Compatibilidad Multimodelo:** Soporte para arquitecturas GGUF, EXL2 y Transformers mediante integraciones con backends populares.
* **Arquitectura Modular:** Separación clara entre el motor de ejecución y la lógica de control.
* **Bajo Consumo de Recursos:** Optimizado para ejecutarse en hardware de consumo (GPUs NVIDIA, Apple Silicon y CPU).

## 🛠️ Requisitos Previos

Antes de instalar, asegúrate de tener:
* **Python 3.10+**
* **CUDA Toolkit** (si usas GPUs NVIDIA)
* **Gestor de paquetes:** `pip` o `conda`

## 📦 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Dertgzgz/localbraincontrol.git
   cd localbraincontrol
   ```

2. **Crear un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏗️ Arquitectura del Backend

El backend está organizado de manera modular para facilitar el mantenimiento y la escalabilidad:

```
backend/
├── main.py              # Punto de entrada de FastAPI
├── config.py            # Configuraciones y utilidades (logging, persistencia)
├── dependencies.py      # Dependencias FastAPI (autenticación)
├── models/
│   ├── __init__.py
│   └── schemas.py       # Modelos Pydantic
├── routers/
│   ├── auth_router.py   # Rutas de autenticación
│   ├── agent_router.py  # Rutas del agente de IA
│   ├── system_router.py # Rutas de métricas del sistema
│   └── config_router.py # Rutas de configuración
└── utils/
    ├── __init__.py
    └── security.py      # Funciones de seguridad (encriptación, JWT)
```

### Ejecutar el Servidor
```bash
python run_server.py
```

El servidor se ejecutará en `http://localhost:8000` con documentación automática en `/docs`.
```

## 🖥️ Uso Técnico

Para iniciar el controlador principal del sistema:

```bash
python main.py --config config.yaml
```

### Integración de API
El sistema expone un endpoint local (compatible con la API de OpenAI por defecto) para conectar herramientas externas como LangChain o interfaces web:

```python
import openai

openai.api_base = "http://localhost:8080/v1"
openai.api_key = "local"

response = openai.ChatCompletion.create(
  model="local-brain",
  messages=[{"role": "user", "content": "¿Cómo optimizo mi flujo de trabajo?"}]
)
```

## 🤝 Contribuciones

Las contribuciones son lo que hacen que la comunidad de código abierto sea un lugar increíble para aprender, inspirar y crear. Cualquier contribución que hagas será **muy apreciada**.

1. Fork del proyecto.
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`).
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4. Push a la rama (`git push origin feature/AmazingFeature`).
5. Abre un Pull Request.

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.

---

**Nota:** Este README asume una estructura estándar basada en los archivos detectados en el repositorio. Si el proyecto tiene scripts específicos de inicialización, se recomienda añadirlos en la sección de "Instalación".