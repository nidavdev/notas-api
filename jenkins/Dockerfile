FROM jenkins/jenkins:lts-jdk17

USER root

# Cliente de Docker y plugin de Compose (copiados de la imagen oficial docker:cli)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:27-cli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

# Plugins definidos en plugins.txt
COPY plugins.txt /usr/share/jenkins/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/plugins.txt

# Configuración como código: usuario administrador y credenciales (leídas de variables de entorno)
COPY casc.yaml /usr/share/jenkins/casc.yaml
ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/casc.yaml
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Se mantiene root para poder usar el socket de Docker del host (solo para entornos de práctica)
