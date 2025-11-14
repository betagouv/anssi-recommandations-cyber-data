from pathlib import Path
import csv
import datetime as dt
import re
from typing import (
    Protocol,
    Final,
    Union,
)
import httpx
from pydantic import BaseModel
from configuration import MQC
from lecteur_csv import LecteurCSV
import asyncio


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


HTTP_SCHEMA: Final[str] = "https"


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
    async def pose_question_async(self, question: str) -> ReponseQuestion: ...


class HorlogeSysteme:
    def aujourd_hui(self) -> str:
        return str(dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


class ClientMQCHTTPAsync:
    def __init__(self, cfg: MQC, client: httpx.AsyncClient | None = None) -> None:
        self._base = construit_base_url(cfg)
        self._route = formate_route_pose_question(cfg)
        self._client = client or httpx.AsyncClient()
        self.delai_attente_maximum = cfg.delai_attente_maximum

    async def pose_question_async(self, question: str) -> ReponseQuestion:
        try:
            reponse = await self._client.post(
                f"{self._base}{self._route}",
                json={"question": question},
                timeout=self.delai_attente_maximum,
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Serveur MQC injoignable: {e}") from e
        reponse.raise_for_status()
        donnees = reponse.json()
        return ReponseQuestion(**donnees)


class RemplisseurReponses:
    def __init__(self, client: InterfaceQuestions) -> None:
        self._client = client

    async def traite_lot_parallele(
        self, questions: list[str], max_workers: int
    ) -> list[dict[str, Union[str, int, float]]]:
        async def traite_question(question: str) -> dict[str, Union[str, int, float]]:
            reponse_question = await self._client.pose_question_async(question)
            return {"Réponse Bot": reponse_question.reponse}

        taches = [traite_question(q) for q in questions]
        resultats = await asyncio.gather(*taches)
        return resultats

    async def remplit_lot_lignes(
        self, lecteur: LecteurCSV, taille_lot: int
    ) -> list[dict[str, Union[str, int, float]]]:
        lignes = []
        questions = []
        for _ in range(taille_lot):
            try:
                ligne = lecteur.ligne_suivante()
                lignes.append(ligne)
                questions.append(str(ligne["Question type"]))
            except StopIteration:
                break

        if not lignes:
            return []

        reponses = await asyncio.gather(
            *[self._client.pose_question_async(q) for q in questions]
        )

        lignes_enrichies = []
        for ligne, reponse_question in zip(lignes, reponses):
            ligne_enrichie = lecteur.appliquer_calcul_ligne(
                "Réponse Bot", lambda _: reponse_question.reponse, ligne
            )

            contexte = (
                ""
                if not reponse_question.paragraphes
                else "${SEPARATEUR_DOCUMENT}".join(
                    [p.contenu for p in reponse_question.paragraphes]
                )
            )
            ligne_enrichie = lecteur.appliquer_calcul_ligne(
                "Contexte", lambda _: contexte, ligne_enrichie
            )

            ligne_enrichie = lecteur.appliquer_calcul_ligne(
                "Noms Documents",
                lambda _: [p.nom_document for p in reponse_question.paragraphes],
                ligne_enrichie,
            )

            ligne_enrichie = lecteur.appliquer_calcul_ligne(
                "Numéros Page",
                lambda _: [p.numero_page for p in reponse_question.paragraphes],
                ligne_enrichie,
            )

            lignes_enrichies.append(ligne_enrichie)

        return lignes_enrichies


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
