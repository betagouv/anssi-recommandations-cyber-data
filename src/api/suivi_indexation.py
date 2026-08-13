from dataclasses import dataclass
from uuid import uuid4

from documents.indexeur.indexeur import (
    ReponseDocument,
    ReponseDocumentEnErreur,
    ReponseDocumentIndexePartiellement,
)


@dataclass
class SuiviIndexation:
    statut: str
    erreurs: list[dict[str, str]]
    documents_partiels: list[dict[str, object]]


_suivis_indexation: dict[str, SuiviIndexation] = {}


def cree_un_suivi() -> str:
    identifiant_operation = uuid4().hex
    _suivis_indexation[identifiant_operation] = SuiviIndexation(
        statut="en_cours", erreurs=[], documents_partiels=[]
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
    suivi.documents_partiels = [
        {
            "document": resultat.nom,
            "id": resultat.id,
            "pages_non_indexees": list(resultat.pages_non_indexees),
            "erreurs": list(resultat.erreurs),
        }
        for resultat in resultats
        if isinstance(resultat, ReponseDocumentIndexePartiellement)
    ]
    if suivi.erreurs:
        suivi.statut = "terminee_avec_erreurs"
    elif suivi.documents_partiels:
        suivi.statut = "terminee_partiellement"
    else:
        suivi.statut = "terminee"


def termine_le_suivi_avec_une_erreur(
    identifiant_operation: str,
    erreur: Exception,
) -> None:
    suivi = _suivis_indexation[identifiant_operation]
    suivi.statut = "terminee_avec_erreurs"
    suivi.erreurs = [{"document": "indexation", "detail": str(erreur)}]
    suivi.documents_partiels = []


def recupere_un_suivi(identifiant_operation: str) -> SuiviIndexation | None:
    return _suivis_indexation.get(identifiant_operation)
