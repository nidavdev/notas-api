import os
import time

import psycopg2
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="/static")

# La conexión usa el nombre de servicio de Docker Compose ("db")
# Usuario, contraseña y nombre de la base vienen de variables de entorno (archivo .env)
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "dbname": os.environ["POSTGRES_DB"],
    "user": os.environ["POSTGRES_USER"],
    "password": os.environ["POSTGRES_PASSWORD"],
    "connect_timeout": 5,
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def init_db(attempts=15, delay=2):
    """Crea la tabla si no existe. Reintenta por si la base aún está arrancando."""
    for attempt in range(1, attempts + 1):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL DEFAULT '',
                        created_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                    """
                )
            conn.close()
            print(f"Conectado a PostgreSQL en '{DB_CONFIG['host']}'", flush=True)
            return
        except psycopg2.OperationalError as e:
            print(f"Esperando a la base de datos ({attempt}/{attempts}): {e}", flush=True)
            time.sleep(delay)
    raise RuntimeError("No se pudo conectar a la base de datos")


@app.get("/")
def index():
    return send_from_directory(app.root_path, "index.html")


@app.get("/health")
def health():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return jsonify(status="ok", database=DB_CONFIG["host"])
    except psycopg2.Error:
        return jsonify(status="error"), 503


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()

    if not title:
        return jsonify(error="El título es obligatorio."), 400
    if len(title) > 100:
        return jsonify(error="El título no puede pasar de 100 caracteres."), 400

    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (title, content) VALUES (%s, %s) "
                "RETURNING id, title, content, created_at",
                (title, content),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    return jsonify(_to_dict(row)), 201


@app.get("/notes")
def list_notes():
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC")
            rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify([_to_dict(r) for r in rows])


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    conn = get_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
            deleted = cur.rowcount
    finally:
        conn.close()

    if deleted == 0:
        return jsonify(error="La nota no existe."), 404
    return "", 204


def _to_dict(row):
    return {
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "created_at": row[3].strftime("%Y-%m-%d %H:%M:%S"),
    }


init_db()
