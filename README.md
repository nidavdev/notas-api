# API de Notas
Aplicación web para guardar notas de texto. Usa dos contenedores de Docker: la API (Flask, Python), que muestra la página y atiende las peticiones, y la base de datos (PostgreSQL), donde se guardan las notas.

## Requisitos
Docker Desktop (en Linux, Docker Engine con Compose v2) y un navegador.

## Ejecutar
Abrir Docker Desktop y esperar a que esté en ejecución. Luego, desde la carpeta del proyecto, crear el archivo `.env` a partir de la plantilla:

```bash
cp .env.example .env
```

En PowerShell: `Copy-Item .env.example .env`

Abre `.env` y cambia `POSTGRES_PASSWORD` por una contraseña propia. Después se deben levantar los contenedores:

```bash
docker compose up --build
```

Cuando aparezca el mensaje `Conectado a PostgreSQL en 'db'`, abrir http://localhost:5000 en el navegador.

## Probar
Con la aplicación abierta, comprobar lo siguiente:

- Bajo el título aparece en verde "Conectado a la base de datos (db)".
- Al escribir un título y un contenido y pulsar "Guardar nota", aparece "Nota guardada." y la nota en la lista.
- Al pulsar "Guardar nota" con el título vacío, aparece un aviso pidiendo el título.
- Al pulsar "Eliminar" en una nota, desaparece de la lista.
- Después de ejecutar `docker compose down` y luego `docker compose up`, las notas siguen ahí porque se guardan en un volumen.

Para comprobar que la API encuentra la base de datos por el nombre del servicio (`db`) y no por `localhost` ni una IP:

```bash
docker compose exec api python -c "import socket; print(socket.gethostbyname('db'))"
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT * FROM notes;"'
```

El primer comando muestra la dirección interna que Docker asigna a `db`. El segundo muestra las mismas notas que fueron guardadas desde la página.

## Detener
```bash
docker compose down
```
Apaga los contenedores y conserva las notas. Para borrarlas usar `docker compose down -v`.

## Configuración
Las variables están en `.env`: `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB` definen las credenciales de la base de datos, y `API_PORT` es el puerto del computador donde se abre la aplicación (por defecto 5000).

Si se cambian las credenciales después de haber levantado la aplicación una vez, ejecuta `docker compose down -v` antes de volver a levantarla, porque la base de datos conserva los valores anteriores en el volumen.

## Problemas frecuentes
- Si aparece `Falta POSTGRES_PASSWORD en el archivo .env`, falta crear el `.env` con `cp .env.example .env`.
- Si aparece `Cannot connect to the Docker daemon`, Docker Desktop no está abierto.
- Si aparece `port is already allocated`, el puerto 5000 está ocupado. Cambia `API_PORT=5001` en `.env` y abre http://localhost:5001.
- Si la página no carga justo después de `up`, espera unos segundos: la API espera a que la base de datos esté lista.
- Si el indicador sale en rojo, revisa `docker compose logs db`. Si cambiaste credenciales, aplica `docker compose down -v`.

Comandos útiles: `docker compose ps` muestra el estado, `docker compose logs -f api` sigue los logs de la API y `docker compose up -d --build` levanta todo en segundo plano.

## Estructura

```
app/
  app.py -> API y conexión a PostgreSQL
  index.html -> página web
  requirements.txt -> dependencias
  static/ -> style.css y script.js
.github/workflows/ci.yml
Dockerfile
docker-compose.yml
.env.example -> plantilla de variables
.env -> credenciales del usuario
```

Rutas de la API: `GET /` (página), `POST /notes` (guardar; `title` es obligatorio), `GET /notes` (listar), `DELETE /notes/<id>` (eliminar) y `GET /health` (estado de la API y la base de datos).
