from adaptateurs.client_albert_chunks import ReponseChunkAlbert
from documents.service_exploration_chunks import ServiceExplorationChunks


def test_restitue_les_chunks_du_document_demande(un_client_albert_chunks):
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

    resultat = service.les_chunks_du_document("document-42")

    assert resultat == [
        ReponseChunkAlbert(
            id="chunk-1",
            contenu="Un contenu",
            metadonnees={"page": 3},
        )
    ]
