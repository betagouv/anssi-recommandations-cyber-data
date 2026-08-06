from dataclasses import dataclass
from uuid import uuid4

from documents.indexeur.indexeur import ReponseDocument, ReponseDocumentEnErreur


@dataclass
class SuiviIndexation:
    statut: str
    erreurs: list[dict[str, str]]


_suivis_indexation: dict[str, SuiviIndexation] = {}


def cree_un_suivi() -> str:
    identifiant_operation = uuid4().hex
    _suivis_indexation[identifiant_operation] = SuiviIndexation(
        statut="en_cours", erreurs=[]
    )
    return identifiant_operation


def termine_le_suivi(
    identifiant_operation: str,
    resultats: list[ReponseDocument],
) -> None:
    suivi = _suivis_indexation[identifiant_operation]
    suivi.erreurs = [
        {
            "document": resultat.document_en_erreur,
            "detail": resultat.detail,
        }
        for resultat in resultats
        if isinstance(resultat, ReponseDocumentEnErreur)
    ]
    suivi.statut = "terminee_avec_erreurs" if suivi.erreurs else "terminee"


def termine_le_suivi_avec_une_erreur(
    identifiant_operation: str,
    erreur: Exception,
) -> None:
    suivi = _suivis_indexation[identifiant_operation]
    suivi.statut = "terminee_avec_erreurs"
    suivi.erreurs = [{"document": "indexation", "detail": str(erreur)}]


def recupere_un_suivi(identifiant_operation: str) -> SuiviIndexation | None:
    return _suivis_indexation.get(identifiant_operation)
