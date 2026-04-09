from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from jeopardy.service import CollectionEntiere, ListeDeDocuments
from jeopardy.service_jeopardyse_collection_entiere import (
    ServiceJeopardyseCollectionEntiere,
    fabrique_service_jeopardise_collection_entiere,
)
from jeopardy.service_jeopardyse_liste_de_documents import (
    ServiceJeopardyseDocuments,
    fabrique_service_jeopardise_documents,
)

api_jeopardy = APIRouter(prefix="/jeopardy")


class RequeteJeopardy(BaseModel):
    id_collection: str
    nom_collection: str
    description_collection: str


@api_jeopardy.post("/", status_code=200)
def jeopardy(
    requete: RequeteJeopardy,
    background_tasks: BackgroundTasks,
    service_jeopardy: ServiceJeopardyseCollectionEntiere = Depends(
        fabrique_service_jeopardise_collection_entiere
    ),  # type: ignore[assignment]
):
    background_tasks.add_task(
        service_jeopardy.jeopardyse,
        CollectionEntiere(
            nom_collection=requete.nom_collection,
            description_collection=requete.description_collection,
            id_collection=requete.id_collection,
        ),
    )
    return {"message": "Jeopardy en cours d’exécution..."}


class RequeteDocumentsJeopardy(BaseModel):
    documents: list[str]
    identifiant_collection: str


@api_jeopardy.post("/{id_collection_jeopardy}/documents", status_code=200)
def jeopardyse_documents_collection(
    requete: RequeteDocumentsJeopardy,
    id_collection_jeopardy: str,
    background_tasks: BackgroundTasks,
    service_jeopardy: ServiceJeopardyseDocuments = Depends(  # type: ignore[assignment]
        fabrique_service_jeopardise_documents
    ),
):
    background_tasks.add_task(
        service_jeopardy.jeopardyse,
        ListeDeDocuments(
            noms_documents=requete.documents,
            id_collection_jeopardy=id_collection_jeopardy,
            id_collection_mqc=requete.identifiant_collection,
        ),
    )
    return {
        "message": f"Ajout des documents de la collection {requete.identifiant_collection} dans la collection {id_collection_jeopardy} en cours d’exécution..."
    }
