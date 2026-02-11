FROM python:3.13-slim

WORKDIR /app

# Evitamos archivos temporales que hinchen la imagen
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Solo lo estrictamente necesario para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Primero instalamos pip y torch (la parte más pesada)
RUN pip install --upgrade pip
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Luego el resto de dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Finalmente el código
COPY . .

# Comando de ejecución limpio
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "8080", "--use-google", "--model", "gemini-2.5-flash"]
