from fastapi.testclient import TestClient

from adaptateurs.client_albert_chunks import ReponseChunkAlbert
from documents.service_exploration_chunks import (
    ServiceExplorationChunks,
    fabrique_service_exploration_chunks,
)


def test_retourne_les_chunks_du_document_demande(
    un_serveur_de_test_pour_collections,
    un_client_albert_chunks,
):
    client_albert = un_client_albert_chunks().avec_les_chunks_du_document(
        "document-42",
        [
            ReponseChunkAlbert(
                id="chunk-1",
                contenu="Un contenu",
                metadonnees={"page": 3},
            )
        ],
    )
    service = ServiceExplorationChunks(client_albert)
    serveur, *_ = un_serveur_de_test_pour_collections()
    serveur.dependency_overrides[fabrique_service_exploration_chunks] = lambda: service
    client = TestClient(serveur)

    reponse = client.get(
        "/api/documents/document-42/chunks",
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.json() == {
        "chunks": [
            {
                "id": "chunk-1",
                "contenu": "Un contenu",
                "contexte_documentaire": None,
                "metadonnees": {"page": 3},
            }
        ]
    }


def test_protege_l_exploration_des_chunks(
    un_serveur_de_test_pour_collections,
):
    serveur, *_ = un_serveur_de_test_pour_collections()
    client = TestClient(serveur)

    reponse = client.get("/api/documents/document-42/chunks")

    assert reponse.status_code == 401
