#!/bin/bash

# Script para deployment rápido de RAG Assistant en Docker

set -e

echo "🚀 RAG Assistant - Docker Deployment Script"
echo "==========================================="
echo ""

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar que Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Creando desde .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Archivo .env creado. Por favor configura tus API keys antes de continuar."
        echo "   Edita el archivo .env y luego ejecuta este script nuevamente."
        exit 0
    else
        echo "❌ No se encontró .env.example. Por favor crea un archivo .env manualmente."
        exit 1
    fi
fi

# Verificar que Ollama está corriendo (si no se usa Google)
echo "🔍 Verificando conexión con Ollama..."
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama está corriendo en localhost:11434"
else
    echo "⚠️  No se puede conectar con Ollama en localhost:11434"
    echo "   Si vas a usar Google Gemini, esto no es un problema."
    read -p "   ¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build de la imagen
echo ""
echo "🔨 Construyendo imagen Docker..."
docker-compose build

if [ $? -ne 0 ]; then
    echo "❌ Error al construir la imagen Docker"
    exit 1
fi

echo "✅ Imagen construida exitosamente"

# Iniciar contenedor
echo ""
echo "🚀 Iniciando contenedor..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Error al iniciar el contenedor"
    exit 1
fi

echo "✅ Contenedor iniciado exitosamente"

# Esperar a que el servicio esté listo
echo ""
echo "⏳ Esperando a que el servicio esté listo..."
sleep 5

# Verificar que el contenedor está corriendo
if docker-compose ps | grep -q "Up"; then
    echo "✅ Contenedor corriendo correctamente"
else
    echo "❌ El contenedor no está corriendo. Mostrando logs:"
    docker-compose logs --tail=50
    exit 1
fi

# Mostrar información
echo ""
echo "=========================================="
echo "🎉 RAG Assistant desplegado exitosamente!"
echo "=========================================="
echo ""
echo "📍 URL: http://localhost:7860"
echo ""
echo "🔐 Credenciales por defecto:"
echo "   Usuario: admin"
echo "   Contraseña: admin123"
echo ""
echo "📊 Comandos útiles:"
echo "   Ver logs:     docker-compose logs -f"
echo "   Detener:      docker-compose down"
echo "   Reiniciar:    docker-compose restart"
echo "   Estado:       docker-compose ps"
echo ""
echo "💾 Datos persistentes en volúmenes:"
echo "   - rag-chroma-db (ChromaDB)"
echo "   - rag-data (Documentos)"
echo ""

# Mostrar logs en tiempo real
read -p "¿Deseas ver los logs en tiempo real? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📜 Mostrando logs (Ctrl+C para salir)..."
    echo ""
    docker-compose logs -f
fi
