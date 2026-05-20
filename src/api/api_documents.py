from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from api.securite import fabrique_verifie_token_jwt
from documents.service_indexation_documents import (
    fabrique_service_indexation_de_documents,
    ServiceDIndexation,
)
from infra.logger import log

api_documents = APIRouter(prefix="/documents")


class RequeteIndexationDocument(BaseModel):
    fichiers_ajoutes: list[str] = []
    fichiers_modifies: list[str] = []


@api_documents.post("/", status_code=200)
def indexe_documents(
    background_tasks: BackgroundTasks,
    requete: RequeteIndexationDocument,
    service_indexation_document: ServiceDIndexation = Depends(  # type: ignore[assignment]
        fabrique_service_indexation_de_documents  # type: ignore[assignment]
    ),
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    les_documents = [*requete.fichiers_ajoutes, *requete.fichiers_modifies]
    log(__name__, f"Indexation des documents {les_documents}")
    background_tasks.add_task(
        service_indexation_document.indexe_documents, les_documents
    )
    return {"message": "Indexation en cours d’exécution..."}
