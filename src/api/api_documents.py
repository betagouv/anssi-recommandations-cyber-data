from dataclasses import dataclass
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel

from api.securite import fabrique_verifie_token_jwt
from documents.indexe_documents_rag import fabrique_client_albert
from adaptateurs.clients_albert import ClientAlbertIndexation
from documents.service_collections import (
    ServiceCollections,
    fabrique_service_collections,
    OffsetsCollections,
)
from documents.service_indexation_documents import (
    fabrique_service_indexation_de_documents,
    ServiceIndexationNouveauxDocuments,
)
from documents.indexeur.indexeur import ReponseDocument, ReponseDocumentEnErreur
from infra.logger import log

api_documents = APIRouter(prefix="/documents")


@dataclass
class SuiviIndexation:
    statut: str
    erreurs: list[dict[str, str]]


_suivis_indexation: dict[str, SuiviIndexation] = {}


class RequeteIndexationDocument(BaseModel):
    fichiers_ajoutes: list[str] = []
    fichiers_modifies: list[str] = []
    fichiers_supprimes: list[str] = []
    url_a_ajouter: str | None = None


class RequeteSuppressionDocuments(BaseModel):
    documents: list[str] = []


def _indexe_les_documents_et_met_a_jour_le_suivi(
    service_indexation_document: ServiceIndexationNouveauxDocuments,
    identifiant_operation: str,
    les_documents: list[str],
    documents_a_supprimer: list[str],
    url_a_ajouter: str | None,
):
    suivi = _suivis_indexation[identifiant_operation]
    try:
        resultats: list[ReponseDocument] = service_indexation_document.indexe_documents(
            les_documents,
            documents_a_supprimer,
            url_a_ajouter,
        ) or []
        suivi.erreurs = [
            {
                "document": resultat.document_en_erreur,
                "detail": resultat.detail,
            }
            for resultat in resultats
            if isinstance(resultat, ReponseDocumentEnErreur)
        ]
        suivi.statut = "terminee_avec_erreurs" if suivi.erreurs else "terminee"
    except Exception as erreur:
        suivi.statut = "terminee_avec_erreurs"
        suivi.erreurs = [{"document": "indexation", "detail": str(erreur)}]


@api_documents.post("/", status_code=200)
def indexe_documents(
    background_tasks: BackgroundTasks,
    requete: RequeteIndexationDocument,
    service_indexation_document: ServiceIndexationNouveauxDocuments = Depends(  # type: ignore[assignment]
        fabrique_service_indexation_de_documents  # type: ignore[assignment]
    ),
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    les_documents = list(
        filter(
            lambda doc: doc.endswith(".pdf"),
            [*requete.fichiers_ajoutes, *requete.fichiers_modifies],
        )
    )
    log(__name__, f"Indexation des documents {les_documents}")
    log(__name__, f"Suppression des documents {requete.fichiers_supprimes}")
    identifiant_operation = uuid4().hex
    _suivis_indexation[identifiant_operation] = SuiviIndexation(
        statut="en_cours", erreurs=[]
    )
    background_tasks.add_task(
        _indexe_les_documents_et_met_a_jour_le_suivi,
        service_indexation_document,
        identifiant_operation,
        les_documents,
        list(filter(lambda doc: doc.endswith(".pdf"), requete.fichiers_supprimes)),
        requete.url_a_ajouter,
    )
    return {
        "message": "Indexation en cours d’exécution...",
        "identifiant_operation": identifiant_operation,
    }


@api_documents.get("/indexation/{identifiant_operation}", status_code=200)
def recupere_le_suivi_de_l_indexation(
    identifiant_operation: str,
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    suivi = _suivis_indexation.get(identifiant_operation)
    if suivi is None:
        raise HTTPException(status_code=404, detail="Identifiant de suivi inconnu")
    return {"statut": suivi.statut, "erreurs": suivi.erreurs}


@api_documents.post("/supprimer", status_code=200)
def supprime_documents_indexation(
    requete: RequeteSuppressionDocuments,
    client_albert: ClientAlbertIndexation = Depends(  # type: ignore[assignment]
        fabrique_client_albert  # type: ignore[assignment]
    ),
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    for document in requete.documents:
        client_albert.supprime_document(document)

    log(__name__, f"Suppression des documents {requete.documents}")

    return {"message": "Suppression en cours d’exécution..."}


@api_documents.get("/", status_code=200)
def recupere_documents(
    indexee: int,
    jeopardy: int,
    id_collection_indexee: str | None = None,
    id_collection_jeopardy: str | None = None,
    service: ServiceCollections = Depends(fabrique_service_collections),  # type: ignore[assignment]
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    les_documents = service.les_documents(
        OffsetsCollections(indexee=indexee, jeopardy=jeopardy),
        id_collection_indexee,
        id_collection_jeopardy,
    )
    return {
        "indexee": [doc._asdict() for doc in les_documents.indexee],
        "jeopardy": [doc._asdict() for doc in les_documents.jeopardy],
    }
