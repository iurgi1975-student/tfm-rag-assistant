# Docker Deployment Guide - RAG Assistant

## 🐳 Deployment Local con Docker

### Requisitos Previos
- Docker y Docker Compose instalados
- Ollama corriendo en tu máquina local (puerto 11434)
- Google API Key configurada

### 📝 Configuración

1. **Configura las variables de entorno** en tu archivo `.env`:
```bash
GOOGLE_API_KEY=tu_api_key_aqui
GRADIO_AUTH_USERS=admin:admin123,user:pass123
```

2. **Construir la imagen Docker**:
```bash
docker-compose build
```

3. **Iniciar el contenedor**:
```bash
docker-compose up -d
```

4. **Ver logs**:
```bash
docker-compose logs -f rag-app
```

5. **Acceder a la aplicación**:
Abre tu navegador en: http://localhost:7860

### 🔐 Login
- Usuario por defecto: `admin`
- Contraseña por defecto: `admin123`

Puedes configurar múltiples usuarios en `.env`:
```bash
GRADIO_AUTH_USERS=usuario1:pass1,usuario2:pass2
```

### 📊 Gestión del Contenedor

**Detener el contenedor**:
```bash
docker-compose down
```

**Reiniciar el contenedor**:
```bash
docker-compose restart
```

**Ver estado**:
```bash
docker-compose ps
```

**Eliminar todo (incluidos volúmenes)**:
```bash
docker-compose down -v
```

### 💾 Persistencia de Datos

Los datos se guardan en volúmenes Docker nombrados:
- `rag-chroma-db`: Base de datos vectorial ChromaDB
- `rag-data`: Documentos y datos de la aplicación
- `./logs`: Logs de la aplicación (montados desde el host)

Los datos persisten incluso si detienes o eliminas el contenedor (excepto si usas `-v`).

### 🔧 Configuración Avanzada

#### Cambiar el puerto
Edita `docker-compose.yml`:
```yaml
ports:
  - "8080:7860"  # Puerto_Host:Puerto_Contenedor
```

#### Usar Ollama en lugar de Google Gemini
En `docker-compose.yml`, cambia el CMD en el Dockerfile o agrega:
```yaml
command: ["python", "app.py", "--host", "0.0.0.0"]
```

Y en la aplicación usa el flag sin `--use-google`.

#### Conectar con Ollama en contenedor
Si tienes Ollama en Docker, modifica la red:
```yaml
environment:
  - OLLAMA_URL=http://ollama:11434
```

Y añade el servicio Ollama a la misma red.

### 🐛 Troubleshooting

**Error: No se puede conectar a Ollama**
- Verifica que Ollama esté corriendo: `curl http://localhost:11434`
- En Windows/Mac, `host.docker.internal` debe funcionar automáticamente
- En Linux, usa `--network host` o configura la red correctamente

**Error: Puerto 7860 ya en uso**
```bash
# Encuentra el proceso usando el puerto
netstat -ano | findstr :7860  # Windows
lsof -i :7860                 # Mac/Linux

# Mata el proceso o cambia el puerto en docker-compose.yml
```

**Error: GOOGLE_API_KEY no encontrada**
- Verifica que el archivo `.env` existe en el directorio raíz
- Asegúrate de que Docker Compose está cargando el .env
- Prueba pasar la variable directamente: `docker-compose run -e GOOGLE_API_KEY=xxx rag-app`

**Los datos se borran al reiniciar**
- Verifica que los volúmenes estén creados: `docker volume ls`
- No uses `docker-compose down -v` a menos que quieras borrar los datos

### 📦 Comandos Útiles

```bash
# Construir sin caché
docker-compose build --no-cache

# Ver logs en tiempo real
docker-compose logs -f

# Ejecutar comando dentro del contenedor
docker-compose exec rag-app bash

# Ver volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect rag-chroma-db

# Backup de datos
docker run --rm -v rag-chroma-db:/data -v $(pwd):/backup alpine tar czf /backup/chroma-backup.tar.gz /data
```


### 🌐 Acceso desde Red Local

Para acceder desde otros dispositivos en tu red:
```yaml
environment:
  - HOST=0.0.0.0  # Ya está configurado por defecto
```

Luego accede desde: `http://TU_IP_LOCAL:7860`

