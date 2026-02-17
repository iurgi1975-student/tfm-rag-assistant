# 🤖 RAG AI Assistant
(La presentación esta creada en la nube de Presentaciones de Google, y compartida con Brice: https://docs.google.com/presentation/d/1TPeGEcbhpuQ1nhj-gsxKkaZkru7Gx5PqEG_x_NhyXvE/edit?usp=sharing )

Sistema de Asistente de IA con Recuperación Aumentada por Generación (RAG) construido sobre arquitectura Domain-Driven Design (DDD). Permite interactuar con un modelo de lenguaje de gran escala (LLM) que accede dinámicamente a una base de conocimientos de documentos personalizados y persistentes.

## 📋 Descripción General del Proyecto

Este proyecto implementa un asistente conversacional inteligente que combina:

- **RAG (Retrieval-Augmented Generation)**: Enriquece las respuestas del LLM con contexto relevante extraído de documentos cargados por el usuario
- **Base de datos vectorial**: Almacena y consulta documentos de manera semántica utilizando embeddings
- **Interfaz web interactiva**: Proporciona una experiencia de usuario tipo ChatGPT con Gradio
- **Arquitectura DDD**: Separa claramente las capas de dominio, aplicación, infraestructura e interfaz para un código mantenible y escalable
- **Autenticación**: Sistema de login opcional para controlar el acceso a la aplicación

### Características Principales

✅ Chat conversacional con IA (Google Gemini)  
✅ Carga y procesamiento de documentos PDF  
✅ Búsqueda semántica en base de conocimientos  
✅ Persistencia de conversaciones  
✅ Gestión de base de conocimientos (agregar/limpiar)  
✅ Arquitectura limpia y modular  
✅ Autenticación de usuarios  
✅ Despliegue en Docker y Cloud Run  

---

## 🛠️ Stack Tecnológico

### Lenguaje y Framework Base
- **Python 3.12+**: Lenguaje principal del proyecto
- **Gradio**: Framework para crear interfaces web interactivas

### Inteligencia Artificial y NLP
- **LangChain**: Framework para desarrollo de aplicaciones con LLMs
  - `langchain-core`: Componentes fundamentales
  - `langchain-community`: Integraciones de la comunidad
  - `langchain-huggingface`: Integración con Hugging Face
  - `langchain-ollama`: Soporte para modelos Ollama (opcional)
  - `langchain-openai`: Integración con OpenAI API
- **Google Generative AI**: API de Google Gemini (modelo principal)
- **Sentence Transformers**: Generación de embeddings semánticos
- **OpenAI**: Modelos de lenguaje (soporte alternativo)

### Base de Datos y Persistencia
- **ChromaDB**: Base de datos vectorial para almacenamiento de embeddings
- **SQLite**: Backend de persistencia de ChromaDB

### Procesamiento de Documentos
- **PyPDF**: Extracción y procesamiento de archivos PDF

### Utilidades y Configuración
- **python-dotenv**: Gestión de variables de entorno
- **Pydantic**: Validación de datos y modelos de dominio

### Testing
- **pytest**: Framework de testing
- **pytest-cov**: Cobertura de código
- **pytest-mock**: Mocking en tests

### Containerización y Despliegue
- **Docker**: Containerización de la aplicación
- **Docker Compose**: Orquestación de contenedores
- **Google Cloud Run**: Plataforma de despliegue serverless

### Servicios para Desarrollo Local
- **Ollama**: Servidor de LLM local para ejecutar modelos open-source (llama2, mistral, codellama, etc.)
- **n8n**: Plataforma de automatización de flujos de trabajo con interfaz visual para integrar servicios

---

## 📦 Instalación y Ejecución

### Requisitos Previos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)
- Git
- (Opcional) Docker y Docker Compose
- API Key de Google Gemini

### 1. Instalación Local

#### Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd tfm-rag-assistant
```

#### Crear Entorno Virtual
```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

#### Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# API Keys
GOOGLE_API_KEY=tu_api_key_de_google_gemini

# Configuración de Autenticación (formato: user1:pass1,user2:pass2)
GRADIO_AUTH_USERS=admin:admin123,user:password

# Configuración del Servidor
PORT=7860

# Ollama (opcional, si usas Ollama local en lugar de Google Gemini)
OLLAMA_URL=http://localhost:11434

# n8n (opcional, para automatización)
N8N_URL=http://localhost:5678
```

#### Ejecutar la Aplicación

```bash
# Ejecución básica
python app.py

# Con opciones personalizadas
python app.py --port 7860 --model gemini-2.5-flash --temperature 0.7

# Sin autenticación (desarrollo)
python app.py --no-auth

# Ver todas las opciones
python app.py --help
```

**Opciones de línea de comandos:**
- `--host`: Host del servidor (default: `0.0.0.0`)
- `--port`: Puerto del servidor (default: `8080`)
- `--model`: Modelo a utilizar (default: `gemini-2.5-flash`)
- `--temperature`: Temperatura del modelo (default: `0.7`)
- `--use-google`: Usar Google Gemini (default: activado)
- `--share`: Crear enlace público de Gradio
- `--debug`: Modo debug
- `--no-auth`: Desactivar autenticación

#### Acceder a la Aplicación

Abre tu navegador en: `http://localhost:7860`

---

### 2. Instalación con Docker

#### Construcción de la Imagen
```bash
docker build -t rag-assistant .
```

#### Ejecutar el Contenedor
```bash
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=tu_api_key \
  -e GRADIO_AUTH_USERS=admin:admin123 \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-assistant
```

#### Usando Docker Compose

**Opción 1: Solo la aplicación RAG**
```bash
# Levantar el servicio
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener el servicio
docker-compose down
```

Acceder en: `http://localhost:7860`

**Opción 2: Con Ollama y n8n para desarrollo local**

Este setup incluye:
- **Ollama**: Modelo LLM local (alternativa a Google Gemini)
- **n8n**: Plataforma de automatización de flujos de trabajo
- **RAG App**: La aplicación principal (opcional)

```bash
# Levantar todos los servicios
docker-compose -f docker-compose-ollama-n8n.yml up -d

# Ver logs
docker-compose -f docker-compose-ollama-n8n.yml logs -f

# Ver logs de un servicio específico
docker-compose -f docker-compose-ollama-n8n.yml logs -f ollama
docker-compose -f docker-compose-ollama-n8n.yml logs -f n8n

# Detener todos los servicios
docker-compose -f docker-compose-ollama-n8n.yml down
```

**Acceso a los servicios:**
- **Ollama**: `http://localhost:11434` (API)
- **n8n**: `http://localhost:5678` (UI de automatización)

**Usar Ollama con la aplicación:**

Una vez levantado Ollama, descarga un modelo:
```bash
# Descargar modelo (ejemplo: llama2)
docker exec -it ollama ollama pull llama2

# O usa otros modelos
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull codellama
```

Luego ejecuta la aplicación (fuera de Docker o en otro compose) apuntando a Ollama:
```bash
# Sin usar Google Gemini (usa Ollama local)
python app.py --model llama2 --no-use-google

# Con variable de entorno
OLLAMA_URL=http://localhost:11434 python app.py --model llama2
```

**Configurar n8n con Ollama:**
1. Accede a n8n en `http://localhost:5678`
2. Crea flujos de trabajo que integren Ollama para procesamiento de lenguaje natural
3. Puedes conectar n8n con la aplicación RAG mediante webhooks o APIs

---

### 3. Despliegue en Google Cloud Run

#### Prerrequisitos
- Cuenta de Google Cloud Platform
- Google Cloud SDK instalado
- Proyecto de GCP configurado

#### Despliegue Automático

##### Linux/Mac:
```bash
chmod +x deploy_to_cloudrun.sh
./deploy_to_cloudrun.sh
```

##### Windows PowerShell:
```powershell
.\redeploy_cloudrun.ps1
```

#### Despliegue Manual

```bash
# Configurar el proyecto
gcloud config set project TU_PROJECT_ID

# Construir y subir la imagen
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/rag-assistant

# Desplegar en Cloud Run
gcloud run deploy rag-assistant \
  --image gcr.io/TU_PROJECT_ID/rag-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=tu_api_key,GRADIO_AUTH_USERS=admin:admin123
```

**Documentación adicional:**
- [CLOUDRUN_DEPLOYMENT.md](CLOUDRUN_DEPLOYMENT.md): Guía detallada de despliegue
- [LOGIN_GUIDE.md](LOGIN_GUIDE.md): Configuración de autenticación

---

## 📁 Estructura del Proyecto

El proyecto sigue los principios de **Clean Architecture** y **Domain-Driven Design (DDD)**:

```
tfm-rag-assistant/
├── app.py                          # Punto de entrada de la aplicación
├── requirements.txt                # Dependencias del proyecto
├── pyproject.toml                  # Configuración de herramientas (pytest, coverage)
├── Dockerfile                      # Configuración de Docker
├── docker-compose.yml              # Orquestación RAG app
├── docker-compose-ollama-n8n.yml   # Orquestación con Ollama y n8n (desarrollo local)
├── .env                            # Variables de entorno (no versionado)
│
├── src/                            # Código fuente principal
│   ├── domain/                     # 🟦 Capa de Dominio (independiente)
│   │   ├── models/                 # Modelos de dominio
│   │   │   ├── chat_message.py    # Modelo de mensajes de chat
│   │   │   ├── document.py        # Modelo de documentos
│   │   │   └── search_result.py   # Modelo de resultados de búsqueda
│   │   └── repositories/           # Interfaces (contratos)
│   │       ├── vector_store_repository.py  # Contrato para BD vectorial
│   │       ├── llm_repository.py           # Contrato para LLMs
│   │       └── chat_history_repository.py  # Contrato para historial
│   │
│   ├── application/                # 🟩 Capa de Aplicación (casos de uso)
│   │   ├── container.py            # Inyección de dependencias
│   │   └── services/               # Servicios de aplicación
│   │       ├── chat_service.py     # Lógica de chat conversacional
│   │       ├── rag_service.py      # Lógica de recuperación RAG
│   │       └── document_service.py # Lógica de gestión de documentos
│   │
│   ├── infrastructure/             # 🟨 Capa de Infraestructura (implementaciones)
│   │   ├── llm/                    # Implementaciones de LLMs
│   │   │   ├── google_gemini_llm.py   # Implementación de Google Gemini
│   │   │   └── ollama_llm.py          # Implementación de Ollama
│   │   ├── vector_stores/          # Implementaciones de base de datos vectorial
│   │   │   └── chroma_store.py     # Implementación de ChromaDB
│   │   ├── persistence/            # Persistencia de datos
│   │   │   └── json_chat_history.py   # Historial en JSON
│   │   ├── document_processor.py   # Procesamiento de PDFs
│   │   └── mappers.py             # Mapeo entre capas
│   │
│   └── interface/                  # 🟪 Capa de Interfaz (adaptadores externos)
│       └── gradio_chat.py          # Interfaz web con Gradio
│
├── tests/                          # Tests unitarios y de integración
│   ├── unit/                       # Tests unitarios por capa
│   │   ├── domain/                 # Tests de modelos de dominio
│   │   ├── application/            # Tests de servicios
│   │   └── infrastructure/         # Tests de implementaciones
│   ├── conftest.py                 # Configuración de pytest
│   ├── README.md                   # Documentación de tests
│   └── GUIA_RAPIDA.md             # Guía rápida de testing
│
├── chroma_db/                      # Base de datos vectorial (persistencia)
├── data/                           # Datos de entrada (documentos)
├── docs/                           # Documentos procesados
├── logs/                           # Logs de la aplicación
│
└── Documentación/                  # Documentación adicional
    ├── arquitectura.md             # Descripción de arquitectura
    └── diagrama_de_secuencia.md    # Diagramas de flujo
```

### Descripción de Capas

#### 🟦 Capa de Dominio (`src/domain/`)
Contiene la **lógica de negocio pura** e independiente de frameworks:
- **Modelos**: Entidades y objetos de valor (ChatMessage, Document, SearchResult)
- **Repositories**: Interfaces/contratos para persistencia (no implementaciones)
- Sin dependencias externas

#### 🟩 Capa de Aplicación (`src/application/`)
Orquesta los **casos de uso** del sistema:
- **ChatService**: Gestiona conversaciones con el LLM
- **RAGService**: Orquesta la recuperación de contexto relevante
- **DocumentService**: Gestiona el ciclo de vida de documentos
- **Container**: Inyección de dependencias

#### 🟨 Capa de Infraestructura (`src/infrastructure/`)
Implementa los detalles técnicos:
- **LLMs**: Implementaciones concretas (Google Gemini, Ollama)
- **Vector Stores**: ChromaDB para almacenamiento vectorial
- **Document Processor**: Carga y chunking de PDFs
- **Persistence**: Almacenamiento de historial de chat

#### 🟪 Capa de Interfaz (`src/interface/`)
Adaptadores externos para interacción:
- **Gradio Chat**: Interfaz web interactiva
- Futura: REST API, CLI, etc.

---

## ⚙️ Funcionalidades Principales

### 1. 💬 Chat Conversacional con IA

- **Conversación Natural**: Interacción fluida con el modelo Google Gemini
- **Contexto RAG**: Las respuestas se enriquecen con información de documentos cargados
- **Memoria Conversacional**: Mantiene el contexto de las últimas 10 interacciones
- **Persistencia**: El historial se guarda y se recupera entre sesiones

**Ejemplo de uso:**
```
Usuario: "¿Qué es la arquitectura hexagonal?"
Asistente: [Busca en documentos cargados y responde con contexto relevante]
```

### 2. 📄 Gestión de Documentos

#### Carga de Documentos
- **Formatos soportados**: PDF
- **Procesamiento automático**: Extracción de texto y chunking inteligente
- **Embeddings**: Conversión a vectores para búsqueda semántica
- **Almacenamiento persistente**: Los documentos quedan disponibles entre sesiones

#### Procesamiento
- **Chunking**: División en fragmentos de ~1000 caracteres
- **Overlap**: Solapamiento de 200 caracteres entre chunks
- **Metadatos**: Preserva información de fuente y página

### 3. 🔍 Búsqueda Semántica

- **Búsqueda por similitud**: Encuentra fragmentos relevantes usando embeddings
- **Scoring**: Puntuación de relevancia para cada resultado
- **Top-K**: Retorna los K fragmentos más relevantes (default: 4)
- **Filtrado**: Opción de filtrar por score mínimo

**Funcionalidades de búsqueda:**
- Buscar documentos relevantes para una consulta
- Previsualización de resultados con score
- Identificación de fuente y contexto

### 4. 🧠 Recuperación Aumentada por Generación (RAG)

El flujo RAG funciona así:

1. **Usuario hace una pregunta** → 
2. **Búsqueda semántica** en base de conocimientos →
3. **Recuperación de contexto** relevante →
4. **Construcción de prompt** enriquecido →
5. **Generación de respuesta** por el LLM →
6. **Respuesta contextualizada** al usuario

**Ventajas:**
- Respuestas basadas en información actualizada y específica
- Reducción de alucinaciones del modelo
- Trazabilidad de fuentes
- Flexibilidad para agregar/modificar conocimiento

### 5. 🔐 Sistema de Autenticación

- **Login opcional**: Puede activarse/desactivarse
- **Múltiples usuarios**: Soporte para varios usuarios con credenciales únicas
- **Variables de entorno**: Configuración segura de credenciales
- **UI de login**: Pantalla de autenticación integrada en Gradio

**Configuración:**
```env
GRADIO_AUTH_USERS="Las verdaderas claves para el acceso a la aplicación están publicadas en la presentación compartida con mouredev@gmail.com"
```

### 6. 📊 Gestión de Base de Conocimientos

- **Estadísticas**: Ver número de documentos almacenados
- **Limpieza**: Borrar toda la base de conocimientos
- **Persistencia**: Los datos persisten en disco (ChromaDB)
- **Escalabilidad**: Diseñado para manejar grandes volúmenes de documentos

### 7. 🎯 Funcionalidades Adicionales

#### Configuración Flexible
- Selección de modelo (Gemini, Ollama)
- Ajuste de temperatura
- Configuración de chunk size y overlap
- Parámetros de RAG (top-k, min-score)

#### Interfaz de Usuario
- **Tabs organizadas**: Chat, Gestión de Documentos, Búsqueda
- **Diseño responsivo**: Adaptado a diferentes tamaños de pantalla
- **Feedback en tiempo real**: Mensajes de estado y error claros
- **Limpieza de historial**: Botón para resetear conversación

#### Logging y Debugging
- Sistema de logs centralizado
- Modo debug para desarrollo
- Mensajes de error descriptivos

---

---

## 🛠️ Desarrollo Local con Ollama y n8n

### ¿Por qué usar Ollama y n8n?

**Ollama** te permite ejecutar modelos LLM localmente sin depender de APIs externas:
- ✅ Sin costos de API
- ✅ Mayor privacidad (datos no salen de tu máquina)
- ✅ Sin límites de requests
- ✅ Funciona sin conexión a internet

**n8n** es una plataforma de automatización que te permite:
- ✅ Crear flujos de trabajo automatizados
- ✅ Integrar múltiples servicios (Ollama, RAG, bases de datos, APIs)
- ✅ Procesar documentos por lotes
- ✅ Crear pipelines de datos complejos

### Setup Completo

1. **Levantar los servicios:**
```bash
docker-compose -f docker-compose-ollama-n8n.yml up -d
```

2. **Descargar modelos en Ollama:**
```bash
# Modelos recomendados
docker exec -it ollama ollama pull llama2        # Modelo general (3.8GB)
docker exec -it ollama ollama pull mistral       # Rápido y eficiente (4.1GB)
docker exec -it ollama ollama pull codellama     # Especializado en código (3.8GB)
docker exec -it ollama ollama pull gemma:2b      # Muy ligero (1.4GB)

# Ver modelos instalados
docker exec -it ollama ollama list
```

3. **Probar Ollama:**
```bash
# Desde terminal
docker exec -it ollama ollama run llama2

# Desde Python
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "¿Qué es la arquitectura DDD?"
}'
```

4. **Ejecutar la app con Ollama:**
```bash
# Ejecutar sin usar Google Gemini
python app.py --model llama2 --temperature 0.7

# La app detectará automáticamente Ollama en localhost:11434
```

5. **Configurar n8n:**
- Accede a `http://localhost:5678`
- Crea tu cuenta (primera vez)
- Explora los workflows de ejemplo

### Casos de Uso con n8n

**1. Procesamiento de documentos por lotes:**
```
Trigger (cada hora) → Leer carpeta → Procesar PDFs → Enviar a RAG → Notificar
```

**2. Pipeline de chat automatizado:**
```
Webhook → Consultar RAG → Ollama → Formatear respuesta → Enviar email/Slack
```

**3. Monitoreo de base de conocimientos:**
```
Cron → Verificar ChromaDB → Generar estadísticas → Dashboard
```

### Integración n8n + Ollama + RAG

Ejemplo de workflow en n8n:

1. **HTTP Request Node**: Recibe consulta del usuario
2. **Code Node**: Prepara la consulta y contexto
3. **HTTP Request to RAG**: Busca documentos relevantes en tu app
4. **HTTP Request to Ollama**: Genera respuesta con contexto
5. **Respond Node**: Devuelve respuesta formateada

### Ventajas del Stack Local

| Aspecto | Google Gemini | Ollama Local |
|---------|--------------|--------------|
| Costo | Por request | Gratuito |
| Privacidad | Datos en la nube | 100% local |
| Velocidad | Depende de internet | Muy rápido |
| Límites | Sí (RPM/RPD) | Sin límites |
| Modelos | Gemini family | 100+ modelos open-source |
| Setup | API Key | Docker + Modelo |

---

## 🧪 Testing
````
El proyecto incluye una suite completa de tests:

```bash
# Ejecutar todos los tests
pytest

# Con cobertura de código
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/domain/
pytest tests/unit/application/
pytest tests/unit/infrastructure/

# Ver reporte de cobertura
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html # Windows
```

**Documentación de tests:**
- [tests/README.md](tests/README.md): Guía completa de testing
- [tests/GUIA_RAPIDA.md](tests/GUIA_RAPIDA.md): Referencia rápida
- [tests/COVERAGE_REPORT.md](tests/COVERAGE_REPORT.md): Reporte de cobertura

---

## 📚 Documentación Adicional

- **[arquitectura.md](Documentación/arquitectura.md)**: Descripción detallada de la arquitectura
- **[diagrama_de_secuencia.md](Documentación/diagrama_de_secuencia.md)**: Diagramas de flujo y secuencia
- **[esquema.md](esquema.md)**: Diagrama general de ejecución
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)**: Guía de despliegue con Docker
- **[CLOUDRUN_DEPLOYMENT.md](CLOUDRUN_DEPLOYMENT.md)**: Guía de despliegue en Cloud Run
- **[LOGIN_GUIDE.md](LOGIN_GUIDE.md)**: Configuración de autenticación

---

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | API Key de Google Gemini | - |
| `GRADIO_AUTH_USERS` | Usuarios autenticados (formato: `user1:pass1,user2:pass2`) | `admin:admin123` |
| `PORT` | Puerto del servidor | `7860` |
| `OLLAMA_URL` | URL de Ollama (si se usa como LLM local) | `http://localhost:11434` |
| `N8N_URL` | URL de n8n (para integraciones) | `http://localhost:5678` |

### Parámetros de Configuración en Container

El `AppContainer` acepta estos parámetros:

```python
AppContainer(
    model_name="gemini-2.5-flash",    # Modelo a utilizar
    temperature=0.7,                   # Creatividad del modelo (0-1)
    chroma_dir="./chroma_db",         # Directorio de ChromaDB
    google_api_key="...",             # API Key
    use_google=True,                  # Usar Google Gemini
    chunk_size=1000,                  # Tamaño de chunks
    chunk_overlap=200,                # Solapamiento entre chunks
    rag_top_k=4,                      # Documentos a recuperar en RAG
    rag_min_score=0.0,                # Score mínimo de relevancia
    memory_window=10                  # Mensajes en memoria
)
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es parte del curso de Infraestructura y Cloud de BigSchool.

---

## 👥 Autores

Desarrollado como proyecto del Módulo 5 - Infraestructura y Cloud

---

## 🆘 Solución de Problemas

### Error: "GOOGLE_API_KEY not found"
**Solución**: Asegúrate de tener el archivo `.env` con tu API key de Google

### Error al cargar documentos PDF
**Solución**: Verifica que el PDF no esté corrupto y que `pypdf` esté instalado correctamente

### ChromaDB no persiste datos
**Solución**: Verifica permisos de escritura en el directorio `chroma_db/`

### Puerto ya en uso
**Solución**: Cambia el puerto con `--port 7861` o detén el proceso que usa el puerto

### Problemas con Docker en Cloud Run
**Solución**: Consulta [CLOUDRUN_FIX.md](CLOUDRUN_FIX.md) para soluciones específicas

---

## 📞 Soporte

Para preguntas o problemas:
- Revisa la [documentación](Documentación/)
- Consulta los archivos de guía específicos (LOGIN_GUIDE.md, CLOUDRUN_DEPLOYMENT.md, etc.)
- Abre un issue en el repositorio

---

**¡Gracias por usar RAG AI Assistant! 🚀**
