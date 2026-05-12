from fastapi import APIRouter

api_documents = APIRouter(prefix="/documents")


@api_documents.post("/", status_code=200)
def indexe_documents():
    return {"message": "Indexation en cours d’exécution..."}
