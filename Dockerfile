#checkov:skip=CKV_DOCKER_2:Healthcheck géré par l'orchestrateur
#checkov:skip=CKV_DOCKER_3:Utilisateur défini dans l'image de base
FROM ghcr.io/betagouv/lab-anssi-evalap@sha256:a918b96b4b8d48814d485e67b6f96a265530c63928f5adbe2f901d2f718508dc

ENV TZ=Europe/Paris
ENV ENV=prod
ENV PORT=8080
ENV POSTGRES_URL=postgresql://${POSTGRESQL_ADDON_USER}:${POSTGRESQL_ADDON_PASSWORD}@${POSTGRESQL_ADDON_HOST}:${POSTGRESQL_ADDON_PORT}

EXPOSE 8000

CMD ["supervisord", "-c", "/app/supervisord.conf"]