from pathlib import Path
from typing import Any, Mapping, Protocol, Final
import datetime as dt
import httpx
from .configuration import Configuration
from .lecteur_csv import LecteurCSV


HTTP_SCHEMA: Final[str] = "http"


def _normalise_prefix(prefix: str) -> str:
    if not prefix:
        return ""
    return prefix if prefix.startswith("/") else f"/{prefix}"


def construit_base_url(cfg: Configuration) -> str:
    prefix = _normalise_prefix(cfg.mqc.prefix_api)
    return f"{HTTP_SCHEMA}://{cfg.mqc.hote}:{cfg.mqc.port}{prefix}"


def formate_route_pose_question(cfg: Configuration) -> str:
    r = cfg.mqc.route_pose_question
    return r if r.startswith("/") else f"/{r}"


class InterfaceQuestions(Protocol):
    def pose_question(self, question: str) -> str: ...


class HorlogeSysteme:
    def aujourd_hui(self) -> str:
        return str(dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


class ClientMQCHTTP:
    def __init__(self, cfg: Configuration, client: httpx.Client | None = None) -> None:
        self._base = construit_base_url(cfg)
        self._route = formate_route_pose_question(cfg)
        self._client = client or httpx.Client()

    def pose_question(self, question: str) -> str:
        try:
            r = self._client.post(
                f"{self._base}{self._route}", json={"question": question}
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Serveur MQC injoignable: {e}") from e
        r.raise_for_status()
        donnees = r.json()
        reponse = donnees.get("reponse")
        if not isinstance(reponse, str):
            raise ValueError(
                "Réponse HTTP invalide: champ 'reponse' manquant ou non str"
            )
        return reponse


class RemplisseurReponses:
    def __init__(self, client: InterfaceQuestions) -> None:
        self._client = client

    def remplit_fichier(self, chemin_csv: Path) -> LecteurCSV:
        lecteur = LecteurCSV(chemin_csv)

        def genere_reponse_bot(d: Mapping[str, Any]) -> str:
            return self._client.pose_question(str(d["Question type"]))

        lecteur.appliquer_calcul_colonne("Réponse Bot", genere_reponse_bot)
        return lecteur


class EcrivainSortie:
    """Écrit un CSV horodaté dans un sous-dossier de sortie."""

    def __init__(
        self, racine: Path, sous_dossier: Path, horloge: HorlogeSysteme
    ) -> None:
        self._racine = racine
        self._sous_dossier = sous_dossier
        self._horloge: HorlogeSysteme = horloge if horloge else HorlogeSysteme()

    def _nom_fichier(self, prefixe: str) -> str:
        return f"{prefixe}_{self._horloge.aujourd_hui()}.csv"

    def ecrit_fichier_depuis_lecteur_csv(
        self, lecteur: LecteurCSV, prefixe: str
    ) -> Path:
        dossier = self._racine / self._sous_dossier
        dossier.mkdir(parents=True, exist_ok=True)
        chemin = dossier / self._nom_fichier(prefixe)
        lecteur.ecrire_vers(chemin)
        return chemin
