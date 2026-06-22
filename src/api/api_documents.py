from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from api.securite import fabrique_verifie_token_jwt
from documents.service_collections import (
    ServiceCollections,
    fabrique_service_collections,
    OffsetsCollections,
)
from documents.service_indexation_documents import (
    fabrique_service_indexation_de_documents,
    ServiceIndexationNouveauxDocuments,
)
from infra.logger import log

api_documents = APIRouter(prefix="/documents")


class RequeteIndexationDocument(BaseModel):
    fichiers_ajoutes: list[str] = []
    fichiers_modifies: list[str] = []
    fichiers_supprimes: list[str] = []


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
    background_tasks.add_task(
        service_indexation_document.indexe_documents,
        les_documents,
        list(filter(lambda doc: doc.endswith(".pdf"), requete.fichiers_supprimes)),
    )
    return {"message": "Indexation en cours d’exécution..."}


@api_documents.get("/", status_code=200)
def recupere_documents(
    indexee: int,
    jeopardy: int,
    service: ServiceCollections = Depends(fabrique_service_collections),  # type: ignore[assignment]
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    les_documents = service.les_documents(
        OffsetsCollections(indexee=indexee, jeopardy=jeopardy)
    )
    return {
        "indexee": [doc._asdict() for doc in les_documents.indexee],
        "jeopardy": [doc._asdict() for doc in les_documents.jeopardy],
    }
