# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (optimización de caché)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Variable de entorno por default
ENV GEE_PROJECT_ID=""

# FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GEE_PROJECT_ID=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]