from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel

from documents.service_indexation_documents import (
    fabrique_service_indexation_de_documents,
    ServiceDIndexation,
)

api_documents = APIRouter(prefix="/documents")


class RequeteIndexationDocument(BaseModel):
    fichiers_ajoutes: list[str]


@api_documents.post("/", status_code=200)
def indexe_documents(
    requete: RequeteIndexationDocument,
    service_indexation_document: ServiceDIndexation = Depends(  # type: ignore[assignment]
        fabrique_service_indexation_de_documents  # type: ignore[assignment]
    ),
):
    service_indexation_document.indexe_documents(requete.fichiers_ajoutes)
    return {"message": "Indexation en cours d’exécution..."}
