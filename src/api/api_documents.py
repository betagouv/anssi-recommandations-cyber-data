from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, field_validator
from urllib.parse import urlsplit

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
    est_une_url_pdf_distante,
)
from documents.service_exploration_chunks import (
    ServiceExplorationChunks,
    fabrique_service_exploration_chunks,
)
from infra.logger import log
from api.suivi_indexation import (
    cree_un_suivi,
    recupere_un_suivi,
    termine_le_suivi,
    termine_le_suivi_avec_une_erreur,
)

api_documents = APIRouter(prefix="/documents")


def _est_un_pdf(document: str) -> bool:
    url = urlsplit(document)
    chemin = url.path if url.scheme or url.netloc else document
    return chemin.lower().endswith(".pdf")


class RequeteIndexationDocument(BaseModel):
    fichiers_ajoutes: list[str] = []
    fichiers_modifies: list[str] = []
    fichiers_supprimes: list[str] = []
    url_a_ajouter: str | None = None
    id_collection_indexee: str | None = None
    id_collection_jeopardy: str | None = None

    @field_validator("fichiers_ajoutes", "fichiers_modifies")
    @classmethod
    def valide_les_urls_pdf_distantes(cls, documents: list[str]) -> list[str]:
        for document in documents:
            url = urlsplit(document)
            if url.scheme or url.netloc:
                if not est_une_url_pdf_distante(document):
                    raise ValueError("L'URL d'un document distant doit être un PDF HTTP(S)")
        return documents


class RequeteSuppressionDocuments(BaseModel):
    documents: list[str] = []


@api_documents.get("/{id_document}/chunks", status_code=200)
def recupere_les_chunks_du_document(
    id_document: str,
    service: ServiceExplorationChunks = Depends(  # type: ignore[assignment]
        fabrique_service_exploration_chunks  # type: ignore[assignment]
    ),
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    return {
        "chunks": [
            chunk._asdict() for chunk in service.les_chunks_du_document(id_document)
        ]
    }


def _indexe_les_documents_et_met_a_jour_le_suivi(
    service_indexation_document: ServiceIndexationNouveauxDocuments,
    identifiant_operation: str,
    les_documents: list[str],
    documents_a_supprimer: list[str],
    url_a_ajouter: str | None,
    id_collection_indexee: str | None,
    id_collection_jeopardy: str | None,
):
    try:
        resultats = service_indexation_document.indexe_documents(
            les_documents,
            documents_a_supprimer,
            url_a_ajouter,
            id_collection_indexee,
            id_collection_jeopardy,
        ) or []
        termine_le_suivi(identifiant_operation, resultats)
    except Exception as erreur:
        termine_le_suivi_avec_une_erreur(identifiant_operation, erreur)


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
            _est_un_pdf,
            [*requete.fichiers_ajoutes, *requete.fichiers_modifies],
        )
    )
    log(__name__, f"Indexation des documents {les_documents}")
    log(__name__, f"Suppression des documents {requete.fichiers_supprimes}")
    identifiant_operation = cree_un_suivi()
    background_tasks.add_task(
        _indexe_les_documents_et_met_a_jour_le_suivi,
        service_indexation_document,
        identifiant_operation,
        les_documents,
        list(filter(lambda doc: doc.endswith(".pdf"), requete.fichiers_supprimes)),
        requete.url_a_ajouter,
        requete.id_collection_indexee,
        requete.id_collection_jeopardy,
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
    suivi = recupere_un_suivi(identifiant_operation)
    if suivi is None:
        raise HTTPException(status_code=404, detail="Identifiant de suivi inconnu")
    return {
        "statut": suivi.statut,
        "erreurs": suivi.erreurs,
        "documents_partiels": suivi.documents_partiels,
    }


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
