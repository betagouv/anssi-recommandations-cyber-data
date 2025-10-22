from pathlib import Path
from typing import Protocol, Final, Union
import datetime as dt
import httpx
from pydantic import BaseModel
from .configuration import MQC
from .lecteur_csv import LecteurCSV
import re
import csv


class Paragraphe(BaseModel):
    score_similarite: float
    numero_page: int
    url: str
    nom_document: str
    contenu: str


class ReponseQuestion(BaseModel):
    reponse: str
    paragraphes: list[Paragraphe]
    question: str


HTTP_SCHEMA: Final[str] = "http"


def construit_base_url(cfg: MQC) -> str:
    def _normalise_suffixe_api(suffixe: str) -> str:
        if not suffixe:
            return ""
        return suffixe if suffixe.startswith("/") else f"/{suffixe}"

    suffixe = _normalise_suffixe_api(cfg.api_prefixe_route)
    return f"{HTTP_SCHEMA}://{cfg.hote}:{cfg.port}{suffixe}"


def formate_route_pose_question(cfg: MQC) -> str:
    r = cfg.route_pose_question
    return r if r.startswith("/") else f"/{r}"


class InterfaceQuestions(Protocol):
    def pose_question(self, question: str) -> ReponseQuestion: ...


class HorlogeSysteme:
    def aujourd_hui(self) -> str:
        return str(dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


class ClientMQCHTTP:
    def __init__(self, cfg: MQC, client: httpx.Client | None = None) -> None:
        self._base = construit_base_url(cfg)
        self._route = formate_route_pose_question(cfg)
        self._client = client or httpx.Client()
        self.delai_attente_maximum = cfg.delai_attente_maximum

    def pose_question(self, question: str) -> ReponseQuestion:
        try:
            r = self._client.post(
                f"{self._base}{self._route}",
                json={"question": question},
                timeout=self.delai_attente_maximum,
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Serveur MQC injoignable: {e}") from e
        r.raise_for_status()
        donnees = r.json()
        return ReponseQuestion(**donnees)


class RemplisseurReponses:
    def __init__(self, client: InterfaceQuestions) -> None:
        self._client = client

    def remplit_ligne(self, lecteur: LecteurCSV) -> dict[str, Union[str, int, float]]:
        ligne = lecteur.ligne_suivante()

        reponse_question = self._client.pose_question(str(ligne["Question type"]))

        ligne_enrichie = lecteur.appliquer_calcul_ligne(
            "Réponse Bot", lambda d: reponse_question.reponse, ligne
        )

        contexte = (
            ""
            if not reponse_question.paragraphes
            else "${SEPARATEUR_DOCUMENT}".join(
                [p.contenu for p in reponse_question.paragraphes]
            )
        )
        ligne_enrichie = lecteur.appliquer_calcul_ligne(
            "Contexte", lambda d: contexte, ligne_enrichie
        )

        return ligne_enrichie


class EcrivainSortie:
    """Écrit un CSV horodaté dans un sous-dossier de sortie."""

    def __init__(
        self, racine: Path, sous_dossier: Path, horloge: HorlogeSysteme
    ) -> None:
        self._racine = racine
        self._sous_dossier = sous_dossier
        self._horloge: HorlogeSysteme = horloge if horloge else HorlogeSysteme()
        self._chemin_courant: Path | None = None

    @staticmethod
    def _desinfecte_prefixe(prefixe: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "_", prefixe)

    def _nom_fichier(self, prefixe: str) -> str:
        nettoye = self._desinfecte_prefixe(prefixe)
        return f"{nettoye}_{self._horloge.aujourd_hui()}.csv"

    def ecrit_ligne_depuis_lecteur_csv(
        self, ligne: dict[str, Union[str, int, float]], prefixe: str
    ) -> Path:
        if self._chemin_courant is None:
            dossier = self._racine / self._sous_dossier
            dossier.mkdir(parents=True, exist_ok=True)
            self._chemin_courant = (dossier / self._nom_fichier(prefixe)).resolve()
            if dossier not in self._chemin_courant.parents:
                raise ValueError("Chemin de sortie en dehors du dossier autorisé")

        if not self._chemin_courant.exists():
            with open(self._chemin_courant, "w", encoding="utf-8", newline="") as f:
                ecrivain = csv.writer(f)
                ecrivain.writerow(ligne.keys())

        with open(self._chemin_courant, "a", encoding="utf-8", newline="") as f:
            ecrivain = csv.writer(f)
            ecrivain.writerow(ligne.values())

        return self._chemin_courant
