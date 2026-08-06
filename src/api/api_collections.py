from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from api.securite import fabrique_verifie_token_jwt
from documents.service_collections import (
    ServiceCollections,
    fabrique_service_collections,
)
from documents.service_indexation_collections import (
    ServiceIndexationNouvellesCollections,
    DocumentsSources,
    fabrique_service_indexation_collections,
)
from api.suivi_indexation import (
    cree_un_suivi,
    termine_le_suivi,
    termine_le_suivi_avec_une_erreur,
)
from infra.logger import log

api_collections = APIRouter(prefix="/collections")


class RequeteIndexationCollection(BaseModel):
    nom: str
    description: str
    fichiers: list[str] = []


def _indexe_une_collection_et_met_a_jour_le_suivi(
    service: ServiceIndexationNouvellesCollections,
    identifiant_operation: str,
    nom: str,
    description: str,
    sources: DocumentsSources,
) -> None:
    try:
        resultats = service.indexe_documents(nom, description, sources) or []
        termine_le_suivi(identifiant_operation, resultats)
    except Exception as erreur:
        termine_le_suivi_avec_une_erreur(identifiant_operation, erreur)


@api_collections.post("/", status_code=200)
def cree_collection(
    background_tasks: BackgroundTasks,
    requete: RequeteIndexationCollection,
    service: ServiceIndexationNouvellesCollections = Depends(  # type: ignore[assignment]
        fabrique_service_indexation_collections  # type: ignore[assignment]
    ),
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    log(__name__, f"Log l'indexation pour {len(requete.fichiers)} fichiers")
    identifiant_operation = cree_un_suivi()
    background_tasks.add_task(
        _indexe_une_collection_et_met_a_jour_le_suivi,
        service,
        identifiant_operation,
        requete.nom,
        requete.description,
        DocumentsSources(fichiers=requete.fichiers),
    )
    return {
        "message": "Indexation en cours d'exécution...",
        "identifiant_operation": identifiant_operation,
    }


@api_collections.get("/", status_code=200)
def recupere_collections(
    id_collection_indexee: str | None = None,
    id_collection_jeopardy: str | None = None,
    service: ServiceCollections = Depends(fabrique_service_collections),  # type: ignore[assignment]
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    collections = service.les_collections(id_collection_indexee, id_collection_jeopardy)
    return {"indexee": collections.indexee, "jeopardy": collections.jeopardy}


@api_collections.get("/disponibles", status_code=200)
def recupere_collections_disponibles(
    service: ServiceCollections = Depends(fabrique_service_collections),  # type: ignore[assignment]
    _token: str = Depends(fabrique_verifie_token_jwt()),  # type: ignore[assignment]
):
    return {"collections": service.les_collections_disponibles()}
