#checkov:skip=CKV_DOCKER_2:Uniquement utilisé en local pour le dev
#checkov:skip=CKV_DOCKER_3:Uniquement utilisé en local pour le dev
FROM docker.io/python:3.13.5

RUN mkdir /app
WORKDIR /app

VOLUME /app
# Pour s'assurer que le `.venv` du conteneur ne soit pas écrasé par l'absence de `.venv` de l'hôte.
VOLUME /app/.venv

COPY pyproject.toml uv.lock ./

ENV PATH="/app/.venv/bin:$PATH"

RUN pip install uv && \
      uv venv && \
      uv sync
