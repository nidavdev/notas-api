"""Pruebas de humo de la API de notas.

Se ejecutan DENTRO del contenedor `api`:
    docker compose exec -T api python - < tests/smoke_test.py
Solo usa la librería estándar, así que no necesita dependencias extra.
"""
import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:5000"
resultados = []


def llamar(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        BASE + ruta, data=datos, method=metodo,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw else None)


def comprobar(nombre, condicion):
    resultados.append(condicion)
    print(("OK   " if condicion else "FALLA"), nombre, flush=True)


# 1. La API ve la base de datos por el nombre del servicio "db"
estado, cuerpo = llamar("GET", "/health")
comprobar("GET /health responde 200 y apunta a 'db'",
          estado == 200 and cuerpo.get("database") == "db")

# 2. Crear una nota
estado, nota = llamar("POST", "/notes", {"title": "nota de Jenkins", "content": "prueba de humo"})
comprobar("POST /notes crea la nota (201)", estado == 201 and nota.get("title") == "nota de Jenkins")
nota_id = nota.get("id") if isinstance(nota, dict) else None

# 3. Leerla de vuelta (API -> PostgreSQL)
estado, lista = llamar("GET", "/notes")
comprobar("GET /notes devuelve la nota guardada",
          estado == 200 and any(n.get("id") == nota_id for n in lista))

# 4. Validación del título
estado, _ = llamar("POST", "/notes", {"title": "   ", "content": "x"})
comprobar("POST /notes con título vacío devuelve 400", estado == 400)

# 5. Eliminar y comprobar que ya no existe
estado, _ = llamar("DELETE", f"/notes/{nota_id}")
comprobar("DELETE /notes/<id> elimina la nota (204)", estado == 204)
estado, _ = llamar("DELETE", f"/notes/{nota_id}")
comprobar("DELETE repetido devuelve 404", estado == 404)

fallidas = resultados.count(False)
print(f"\n{len(resultados) - fallidas}/{len(resultados)} pruebas correctas", flush=True)
sys.exit(1 if fallidas else 0)
