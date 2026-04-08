from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from jeopardy.service import CollectionEntiere
from jeopardy.service_jeopardyse_collection_entiere import (
    ServiceJeopardyseCollectionEntiere,
    fabrique_service_jeopardise_collection_entiere,
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
