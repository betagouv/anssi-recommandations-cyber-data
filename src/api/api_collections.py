from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from api.securite import fabrique_verifie_token_jwt
from documents.service_indexation_collections import (
    ServiceIndexationNouvellesCollections,
    SourcesDocuments,
    fabrique_service_indexation_collections,
)

api_collections = APIRouter(prefix="/collections")


class RequeteIndexationCollection(BaseModel):
    nom: str
    description: str
    fichiers: list[str] = []
    fichier_documents_distants: str | None = None
    fichier_documents_maitrises: str | None = None


@api_collections.post("/", status_code=200)
def cree_collection(
    background_tasks: BackgroundTasks,
    requete: RequeteIndexationCollection,
    service: ServiceIndexationNouvellesCollections = Depends(  # type: ignore[assignment]
        fabrique_service_indexation_collections  # type: ignore[assignment]
    ),
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    background_tasks.add_task(
        service.indexe_documents,
        requete.nom,
        requete.description,
        SourcesDocuments(
            fichiers=requete.fichiers,
            fichier_documents_distants=requete.fichier_documents_distants,
            fichier_documents_maitrises=requete.fichier_documents_maitrises,
        ),
    )
    return {"message": "Indexation en cours d'exécution..."}
