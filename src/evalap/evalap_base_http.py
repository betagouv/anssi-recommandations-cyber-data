import requests
from typing import Any, Mapping, Optional
from configuration import Configuration


class EvalapBaseHTTP:
    def __init__(self, configuration: Configuration, session: requests.Session) -> None:
        self.evalap_url = configuration.evalap.url
        self.session: requests.Session = session
        authentification = configuration.evalap.token_authentification
        if authentification:
            self.session.headers.update({"Authorization": f"Bearer {authentification}"})

    def _get(self, path: str, *, timeout: float) -> Any:
        r = self.session.get(f"{self.evalap_url}{path}", timeout=timeout)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, json: Mapping[str, object], *, timeout: float) -> Any:
        r = self.session.post(f"{self.evalap_url}{path}", json=json, timeout=timeout)
        r.raise_for_status()
        return r.json()
