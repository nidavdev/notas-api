pipeline {
    agent any

    options {
        // Dos builds a la vez chocarían en el puerto publicado (API_PORT) y en el proyecto de Compose
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // Disparo automático con cada push a GitHub:
    // Poll SCM, Jenkins revisa el repositorio cada 2 minutos (funciona en local)
    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        COMPOSE_PROJECT_NAME = 'notas-ci'
        API_PORT             = '5100'
        POSTGRES_DB          = 'notes_db'

        // Credencial guardada en Jenkins (id: postgres-credentials)
        POSTGRES_CREDS    = credentials('postgres-credentials')
        POSTGRES_USER     = "${POSTGRES_CREDS_USR}"
        POSTGRES_PASSWORD = "${POSTGRES_CREDS_PSW}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Build') {
            steps {
                // Servicio api: se construye desde el Dockerfile
                sh 'docker compose build --pull api'
                // Servicio db: imagen oficial de PostgreSQL (no tiene Dockerfile), se descarga
                sh 'docker compose pull db'
            }
        }

        stage('Test') {
            steps {
                sh 'docker compose up -d --wait --wait-timeout 120'
                sh 'docker compose ps'
                // Pruebas de humo ejecutadas dentro del contenedor api (ver tests/smoke_test.py)
                sh 'docker compose exec -T api python - < tests/smoke_test.py'
            }
        }
    }

    post {
        success {
            echo 'Pipeline correcto: imágenes construidas y API <-> base de datos funcionando.'
        }
        failure {
            echo 'El pipeline falló. Logs de los contenedores:'
            sh 'docker compose logs --no-color || true'
        }
        cleanup {
            // Se ejecuta siempre y al final (después de mostrar los logs)
            sh 'docker compose down -v --remove-orphans || true'
            cleanWs()
        }
    }
}
