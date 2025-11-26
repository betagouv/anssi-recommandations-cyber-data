from typing import (
    Protocol,
    Final,
    Union,
)
import httpx
from pydantic import BaseModel
from configuration import MQC
import asyncio

from infra.lecteur_csv import LecteurCSV


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
    async def pose_question(self, question: str) -> ReponseQuestion: ...


class ClientMQCHTTPAsync:
    def __init__(self, cfg: MQC, client: httpx.AsyncClient | None = None) -> None:
        self._base = construit_base_url(cfg)
        self._route = formate_route_pose_question(cfg)
        self._client = client or httpx.AsyncClient()
        self.delai_attente_maximum = cfg.delai_attente_maximum

    async def pose_question(self, question: str) -> ReponseQuestion:
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
            *[self._client.pose_question(q) for q in questions]
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
