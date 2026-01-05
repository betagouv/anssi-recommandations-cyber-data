from typing import Optional

from requests.models import Response
import requests


class ExecuteurDeRequete:
    def __init__(self):
        super().__init__()
        self.session = None

    def initialise(self, clef_api: str):
        self.session = requests.Session()
        self.session.headers = {"Authorization": f"Bearer {clef_api}"}

    def poste(self, url: str, payload: dict, fichiers: Optional[dict]) -> Response:
        return self.session.post(f"{url}", data=payload, files=fichiers)
