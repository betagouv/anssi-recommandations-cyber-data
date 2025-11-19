#checkov:skip=CKV_DOCKER_2:Healthcheck géré par l'orchestrateur
#checkov:skip=CKV_DOCKER_3:Utilisateur défini dans l'image de base
FROM ghcr.io/betagouv/lab-anssi-evalap@sha256:3f34b938eab7affea49b2b67c95e823263c27f02339f580e2ba4a3eb1b86f02c

ENV TZ=Europe/Paris
ENV ENV=prod
ENV PORT=8080
ENV POSTGRES_URL=postgresql://${POSTGRESQL_ADDON_USER}:${POSTGRESQL_ADDON_PASSWORD}@${POSTGRESQL_ADDON_HOST}:${POSTGRESQL_ADDON_PORT}

EXPOSE 8000

CMD ["supervisord", "-n", "-c", "/app/supervisord.conf", "-l", "/tmp/supervisord.log", "-e", "debug"]