from pathlib import Path
from typing import Any, Mapping, Protocol, Final, Union, Callable
import datetime as dt
import httpx
from pydantic import BaseModel
from .configuration import MQC
from .lecteur_csv import LecteurCSV
import re


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

    def remplit_fichier(self, chemin_csv: Path) -> LecteurCSV:
        lecteur = LecteurCSV(chemin_csv)
        cache_reponses = {}

        def obtient_reponse_question(question: str) -> ReponseQuestion:
            if question not in cache_reponses:
                cache_reponses[question] = self._client.pose_question(question)
            return cache_reponses[question]

        def genere_reponse(
            extracteur: Callable[[ReponseQuestion], str],
        ) -> Callable[[Mapping[str, Union[str, int, float]]], str]:
            def _genere(d: Mapping[str, Union[str, int, float]]) -> str:
                reponse_question = obtient_reponse_question(str(d["Question type"]))
                return extracteur(reponse_question)

            return _genere

        def extrait_reponse(rq: ReponseQuestion) -> str:
            return rq.reponse

        def extrait_paragraphes(rq: ReponseQuestion) -> str:
            if not rq.paragraphes:
                return ""
            return "${SEPARATEUR_DOCUMENT}".join([p.contenu for p in rq.paragraphes])

        lecteur.appliquer_calcul_colonne("Réponse Bot", genere_reponse(extrait_reponse))
        lecteur.appliquer_calcul_colonne(
            "Contexte", genere_reponse(extrait_paragraphes)
        )
        return lecteur

    def remplit_ligne(self, chemin_csv: Path) -> dict[str, Union[str, int, float]]:
        lecteur = LecteurCSV(chemin_csv)
        ligne = next(lecteur.iterer_lignes())

        reponse_question = self._client.pose_question(str(ligne["Question type"]))

        ligne_enrichie = lecteur.appliquer_calcul_ligne(
            "Réponse Bot", lambda d: reponse_question.reponse, ligne
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

    @staticmethod
    def _desinfecte_prefixe(prefixe: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "_", prefixe)

    def _nom_fichier(self, prefixe: str) -> str:
        nettoye = self._desinfecte_prefixe(prefixe)
        return f"{nettoye}_{self._horloge.aujourd_hui()}.csv"

    def ecrit_fichier_depuis_lecteur_csv(
        self, lecteur: LecteurCSV, prefixe: str
    ) -> Path:
        dossier = self._racine / self._sous_dossier
        dossier.mkdir(parents=True, exist_ok=True)
        chemin = (dossier / self._nom_fichier(prefixe)).resolve()
        if dossier not in chemin.parents:
            raise ValueError("Chemin de sortie en dehors du dossier autorisé")
        lecteur.ecrire_vers(chemin)
        return chemin
