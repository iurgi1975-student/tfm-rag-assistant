# 🔥 SOLUCIÓN RÁPIDA - Error de Puerto en Cloud Run

## ❌ El Error

```
The user-provided container failed to start and listen on the port 
defined provided by the PORT=8080 environment variable
```

**Causa**: Cloud Run espera que la aplicación escuche en el puerto **8080**, pero el Dockerfile estaba configurado para **7860**.

## ✅ Solución Aplicada

### Cambios Realizados:

1. **Dockerfile**:
   - ✅ Cambiado `EXPOSE 7860` → `EXPOSE 8080`
   - ✅ Health check actualizado para puerto 8080
   - ✅ Aumentado `start-period` a 60s (la app tarda en iniciar)

2. **deploy_to_cloudrun.sh**:
   - ✅ Cambiado puerto por defecto a 8080
   - ✅ Eliminada variable PORT redundante en env vars

3. **app.py** (ya estaba bien):
   - ✅ Lee `os.getenv("PORT", 7860)` correctamente
   - ✅ Cloud Run asignará PORT=8080 automáticamente

## 🚀 Cómo Re-desplegar

### Opción 1: Script Rápido (Recomendado)

```bash
# Solo reconstruye la imagen con la configuración correcta
chmod +x redeploy_cloudrun.sh
./redeploy_cloudrun.sh
```

### Opción 2: Despliegue Completo

```bash
# Ejecuta el despliegue completo nuevamente
./deploy_to_cloudrun.sh
```

### Opción 3: Comandos Manuales

```bash
PROJECT_ID="tu-proyecto-id"
REGION="us-central1"
SERVICE_NAME="rag-assistant"
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/rag-assistant/rag-assistant:latest"

# 1. Reconstruir imagen
gcloud builds submit --tag="$IMAGE_TAG" --project="$PROJECT_ID"

# 2. Actualizar servicio (si ya existe)
gcloud run services update $SERVICE_NAME \
    --image="$IMAGE_TAG" \
    --region="$REGION" \
    --project="$PROJECT_ID"

# 3. Ver logs
gcloud run services logs read $SERVICE_NAME --region="$REGION" --limit=50
```

## 🔍 Verificar que Funciona

### 1. Ver Logs en Tiempo Real

```bash
gcloud run services logs read rag-assistant \
    --region=us-central1 \
    --follow
```

Deberías ver:
```
🚀 Starting RAG AI Assistant...
📍 Host: 0.0.0.0:8080
🤖 Model: gemini-2.5-flash
...
Running on local URL:  http://0.0.0.0:8080
```

### 2. Verificar Health Check

```bash
# El servicio debe estar "Ready"
gcloud run services describe rag-assistant \
    --region=us-central1 \
    --format="value(status.conditions)"
```

### 3. Probar la URL

```bash
# Obtener URL
SERVICE_URL=$(gcloud run services describe rag-assistant \
    --region=us-central1 \
    --format='value(status.url)')

echo "Tu app está en: $SERVICE_URL"

# Probar que responde
curl -I $SERVICE_URL
```

## 📝 Qué Estaba Desplegando

### Proceso de Cloud Run:

```
1. deploy_to_cloudrun.sh
   ↓
2. gcloud builds submit (usa Cloud Build)
   ↓
3. Cloud Build lee el Dockerfile
   ↓
4. Construye imagen Docker
   ↓
5. Sube a Artifact Registry
   ↓
6. Cloud Run ejecuta la imagen
   ↓
7. Asigna PORT=8080 como variable de entorno
   ↓
8. Tu app debe escuchar en ese puerto
```

### NO Usa:
- ❌ docker-compose.yml (ese es solo para desarrollo local)
- ❌ start.sh (usa el CMD del Dockerfile directamente)
- ❌ Puerto 7860 (Cloud Run prefiere 8080)

### SÍ Usa:
- ✅ Dockerfile
- ✅ requirements.txt
- ✅ Todo el código fuente (src/, app.py, etc.)
- ✅ Variables de entorno de Cloud Run

## 🐛 Troubleshooting

### Si Sigue Sin Funcionar:

1. **Verificar que la imagen se construyó**:
```bash
gcloud artifacts docker images list \
    us-central1-docker.pkg.dev/[PROJECT_ID]/rag-assistant
```

2. **Ver errores de construcción**:
```bash
gcloud builds list --limit=5
gcloud builds describe [BUILD_ID]
```

3. **Aumentar timeout de inicio**:
```bash
gcloud run services update rag-assistant \
    --timeout=600 \
    --region=us-central1
```

4. **Aumentar memoria** (si falla por OOM):
```bash
gcloud run services update rag-assistant \
    --memory=4Gi \
    --region=us-central1
```

5. **Ver logs completos**:
```bash
gcloud run services logs read rag-assistant \
    --region=us-central1 \
    --limit=200
```

## 💡 Configuración Recomendada para Cloud Run

```bash
gcloud run deploy rag-assistant \
    --image=$IMAGE_TAG \
    --region=us-central1 \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0 \
    --port=8080 \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_API_KEY=tu_key,GRADIO_AUTH_USERS=admin:pass123"
```

## ✅ Checklist Post-Fix

- [ ] Dockerfile actualizado (EXPOSE 8080)
- [ ] Script de deploy actualizado
- [ ] Imagen reconstruida en Cloud Build
- [ ] Servicio desplegado/actualizado
- [ ] Logs verificados (sin errores de puerto)
- [ ] URL accesible desde el navegador
- [ ] Login funciona correctamente
- [ ] App responde al health check

---

## 📚 Recursos

- [Cloud Run - Container Port Configuration](https://cloud.google.com/run/docs/configuring/containers#configure-port)
- [Cloud Run - Health Checks](https://cloud.google.com/run/docs/configuring/healthchecks)
- [Troubleshooting Cloud Run](https://cloud.google.com/run/docs/troubleshooting)

¡Con estos cambios tu app debería funcionar correctamente en Cloud Run! 🎉
