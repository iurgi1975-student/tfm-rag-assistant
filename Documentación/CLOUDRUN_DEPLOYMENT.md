# 🌐 Guía de Despliegue en Google Cloud Run

Esta guía te ayudará a desplegar tu RAG Assistant en Google Cloud Run, una plataforma serverless que escala automáticamente según la demanda.

## 📋 Requisitos Previos

### 1. Cuenta de Google Cloud
- Crea una cuenta en [Google Cloud Platform](https://cloud.google.com/)
- Habilita la facturación (Cloud Run tiene un tier gratuito generoso)
- Crea un nuevo proyecto o usa uno existente

### 2. Google Cloud SDK (gcloud CLI)
Instala el CLI de Google Cloud:

**Windows:**
```powershell
# Descarga e instala desde:
# https://cloud.google.com/sdk/docs/install#windows


**Linux/macOS:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### 3. Autenticación
```bash
# Inicia sesión en Google Cloud
gcloud auth login

# Configura la autenticación de Docker
gcloud auth configure-docker
```

### 4. Variables de Entorno
Asegúrate de tener tu `.env` configurado con:
```bash
GOOGLE_API_KEY=tu_google_api_key_aqui
GRADIO_AUTH_USERS=admin:admin123,user:pass456
```


## 📝 Despliegue Manual Paso a Paso

Si prefieres entender cada paso o personalizar el despliegue:

### 1. Configurar el Proyecto

```bash
# Define tu proyecto
PROJECT_ID="tu-proyecto-id"
REGION="us-central1"
SERVICE_NAME="rag-assistant"

# Establece el proyecto
gcloud config set project $PROJECT_ID
```

### 2. Habilitar APIs Necesarias

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com
```

### 3. Crear Repositorio en Artifact Registry

```bash
gcloud artifacts repositories create rag-assistant \
    --repository-format=docker \
    --location=$REGION \
    --description="RAG Assistant Docker images"
```

### 4. Construir la Imagen con Cloud Build

```bash
# Construye y sube la imagen
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/rag-assistant/rag-assistant:latest"

gcloud builds submit \
    --tag=$IMAGE_TAG \
    --timeout=20m
```

### 5. Desplegar en Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0 \
    --port=7860 \
    --set-env-vars="GOOGLE_API_KEY=tu_api_key" \
    --set-env-vars="GRADIO_AUTH_USERS=admin:admin123" \
    --set-env-vars="PORT=7860"
```

### 6. Obtener la URL del Servicio

```bash
gcloud run services describe $SERVICE_NAME \
    --platform=managed \
    --region=$REGION \
    --format='value(status.url)'
```

```

### Configurar Secretos (Recomendado para Producción)

En lugar de pasar la API key como variable de entorno:

```bash
# 1. Crear secret en Secret Manager
echo -n "tu_api_key" | gcloud secrets create google-api-key \
    --data-file=- \
    --replication-policy=automatic

# 2. Dar permisos al servicio de Cloud Run
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding google-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# 3. Desplegar usando el secret
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --set-secrets="GOOGLE_API_KEY=google-api-key:latest" \
    # ... otras opciones
```

## 🔒 Seguridad

### Habilitar Cloud Run Authentication

Si quieres autenticación a nivel de Cloud Run (además de la autenticación de Gradio):

```bash
gcloud run deploy $SERVICE_NAME \
    --no-allow-unauthenticated \
    # ... otras opciones
```

Luego, otorga acceso a usuarios específicos:
```bash
gcloud run services add-iam-policy-binding $SERVICE_NAME \
    --member="user:usuario@ejemplo.com" \
    --role="roles/run.invoker" \
    --region=$REGION
```

### VPC y Redes Privadas

Para conectar con recursos privados:
```bash
gcloud run deploy $SERVICE_NAME \
    --vpc-connector=tu-vpc-connector \
    --vpc-egress=private-ranges-only \
    # ... otras opciones
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
gcloud run services logs read $SERVICE_NAME \
    --region=$REGION \
    --follow
```

### Ver Logs con Filtros

```bash
# Solo errores
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
    --limit=50 \
    --format=json

# Logs de las últimas 24 horas
gcloud logging read "resource.type=cloud_run_revision" \
    --freshness=1d
```

### Métricas en Cloud Console

Visita: `https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics`

Para ver:
- Solicitudes por segundo
- Latencia
- Tasa de error
- Uso de memoria y CPU
- Número de instancias

## 🔄 Actualización del Servicio

### Actualizar con Nueva Versión

```bash
# 1. Construir nueva imagen
gcloud builds submit --tag=$IMAGE_TAG

# 2. Actualizar el servicio (Cloud Run lo hace automáticamente)
# El servicio se actualizará con la imagen :latest

# O especifica una versión nueva:
NEW_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/rag-assistant/rag-assistant:v2"
gcloud builds submit --tag=$NEW_TAG

gcloud run deploy $SERVICE_NAME \
    --image=$NEW_TAG \
    --region=$REGION
```

### Rollback a Versión Anterior

```bash
# Listar revisiones
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION

# Hacer rollback
gcloud run services update-traffic $SERVICE_NAME \
    --to-revisions=REVISION_NAME=100 \
    --region=$REGION
```


## 💰 Costos y Optimización

### Tier Gratuito de Cloud Run
- **2 millones** de solicitudes al mes
- **360,000** GB-segundos de memoria
- **180,000** vCPU-segundos
- Incluye tiempo de red y egress de datos

### Optimizar Costos

1. **Escalar a Cero**: Usa `--min-instances=0` si tu aplicación no requiere estar siempre activa
2. **Timeout Apropiado**: Ajusta `--timeout` según tus necesidades
3. **Recursos Justos**: No sobre-aprovisiones memoria/CPU si no es necesario
4. **Concurrencia**: Aumenta `--concurrency` para manejar más solicitudes por instancia

### Calcular Costos

Usa la [calculadora de precios de Cloud Run](https://cloud.google.com/products/calculator)

Ejemplo estimado:
- 10,000 solicitudes/día
- 30 segundos promedio por solicitud
- 2GB memoria, 2 vCPU
- **~$15-25 USD/mes** (puede variar según región y uso)



