# Jenkins para notas-api

## 1. Levantar Jenkins
```bash
cd jenkins
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
# Edita .env y cambia las contraseñas
docker compose up -d --build
```
Abre http://localhost:8080 e inicia sesión con `JENKINS_ADMIN_ID` / `JENKINS_ADMIN_PASSWORD`.
No aparece el asistente de instalación: los plugins (`plugins.txt`), el usuario y las credenciales
se configuran solos con `casc.yaml`.

## 2. Verificar la instalación
- **Plugins:** Manage Jenkins → Plugins → Installed plugins (Git, GitHub, Pipeline, Credentials Binding, Timestamper, Workspace Cleanup...).
- **Credenciales:** Manage Jenkins → Credentials → *System* → *Global*. Debe existir `postgres-credentials`
  (el valor queda cifrado en Jenkins; no está en el repositorio).

## 3. Crear el job (una sola vez)
1. New Item → nombre `notas-api` → **Pipeline** → OK.
2. En *Pipeline* elige **Pipeline script from SCM** → SCM: **Git**.
3. *Repository URL*: la URL de tu repo en GitHub. Branch: `*/main`. *Script Path*: `Jenkinsfile`.
   - Si el repo es privado: *Add* → Jenkins → "Username with password" (usuario de GitHub + token personal) y selecciónala.
4. Save → **Build Now** (el primer build registra los disparadores definidos en el `Jenkinsfile`).

## 4. Disparo automático con cada push
El `Jenkinsfile` declara `pollSCM('H/2 * * * *')`: Jenkins revisa GitHub cada ~2 minutos y construye si hay un commit nuevo.
Para probarlo: haz un commit, `git push` y espera un par de minutos.

## 5. Seguridad
- `jenkins/.env` está ignorado por Git (`.gitignore` ya excluye `.env`). Solo se sube `.env.example`.
- Montar `/var/run/docker.sock` da a Jenkins control del Docker del equipo: úsalo solo para prácticas.
