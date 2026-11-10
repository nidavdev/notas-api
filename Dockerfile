# Imagen base oficial con versión fija
FROM python:3.12.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero, Docker reutiliza esta capa si requirements.txt no cambia
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la aplicación
COPY app/ .

# No ejecutar como root
RUN useradd --create-home appuser
USER appuser

# Puerto en el que escucha la API
EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "app:app"]
