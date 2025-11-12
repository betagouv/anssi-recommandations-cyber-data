#checkov:skip=CKV_DOCKER_2:Healthcheck géré par l'orchestrateur
#checkov:skip=CKV_DOCKER_3:Utilisateur défini dans l'image de base
FROM ghcr.io/betagouv/lab-anssi-evalap@sha256:e181e634ebbf0620c31c8b059226f216cf128f9938c23eea44973d6ab82cf835

ENV TZ=Europe/Paris
ENV ENV=prod
ENV PORT=8080
ENV POSTGRES_URL=postgresql://${POSTGRESQL_ADDON_USER}:${POSTGRESQL_ADDON_PASSWORD}@${POSTGRESQL_ADDON_HOST}:${POSTGRESQL_ADDON_PORT}

EXPOSE 8000

CMD ["supervisord", "-c", "/app/supervisord.conf"]