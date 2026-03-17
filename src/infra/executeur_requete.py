from typing import Optional

import requests
from requests.models import Response


class ExecuteurDeRequete:
    def __init__(self):
        super().__init__()
        self.session = None

    def initialise_connexion(self):
        self.session = requests.Session()

    def initialise_connexion_securisee(self, clef_api: str):
        self.initialise_connexion()
        self.session.headers = {"Authorization": f"Bearer {clef_api}"}

    def poste(self, url: str, payload: dict, fichiers: Optional[dict]) -> Response:
        if fichiers is not None:
            return self.session.post(f"{url}", data=payload, files=fichiers)
        return self.session.post(f"{url}", json=payload, files=fichiers)

    def recupere(self, url) -> Response:
        return requests.Session().get(url)


def fabrique_executeur_de_requete() -> ExecuteurDeRequete:
    return ExecuteurDeRequete()
