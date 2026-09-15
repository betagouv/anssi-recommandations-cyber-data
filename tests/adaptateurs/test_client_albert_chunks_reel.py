import pytest

from adaptateurs.client_albert_chunks import ReponseChunkAlbert
from adaptateurs.client_albert_chunks_reel import ClientAlbertChunksReel


def test_recupere_les_chunks_d_un_document(un_executeur_albert_memoire):
    executeur = (
        un_executeur_albert_memoire()
        .avec_le_nombre_de_chunks(1)
        .avec_les_pages_de_chunks(
            [
                [
                    {
                        "id": "chunk-1",
                        "content": "Le contenu du chunk",
                        "metadata": {"page": 4},
                    }
                ]
            ]
        )
    )
    client = ClientAlbertChunksReel("https://albert.test/v1", "clef", executeur)

    resultat = client.recupere_les_chunks_du_document("document-42")

    assert resultat == [
        ReponseChunkAlbert(
            id="chunk-1",
            contenu="Le contenu du chunk",
            metadonnees={"page": 4},
        )
    ]


def test_recupere_les_chunks_apres_la_premiere_page(un_executeur_albert_memoire):
    executeur = (
        un_executeur_albert_memoire()
        .avec_le_nombre_de_chunks(101)
        .avec_les_pages_de_chunks(
            [
                [
                    {"id": f"chunk-{index}", "content": "contenu", "metadata": {}}
                    for index in range(100)
                ],
                [{"id": "chunk-100", "content": "contenu", "metadata": {}}],
            ]
        )
    )
    client = ClientAlbertChunksReel("https://albert.test/v1", "clef", executeur)

    resultat = client.recupere_les_chunks_du_document("document-42")

    assert resultat[100].id == "chunk-100"


@pytest.mark.parametrize(
    ("nombre_de_chunks", "nombre_de_requetes_attendu"),
    [(0, 0), (1, 1), (100, 1), (101, 2), (200, 2), (201, 3)],
)
def test_demande_les_pages_necessaires_selon_le_nombre_de_chunks(
    un_executeur_albert_memoire, nombre_de_chunks, nombre_de_requetes_attendu
):
    executeur = (
        un_executeur_albert_memoire()
        .avec_le_nombre_de_chunks(nombre_de_chunks)
        .avec_les_pages_de_chunks([[] for _ in range(nombre_de_requetes_attendu)])
    )
    client = ClientAlbertChunksReel("https://albert.test/v1", "clef", executeur)

    client.recupere_les_chunks_du_document("document-42")

    assert len(executeur.requetes_de_chunks_recues) == nombre_de_requetes_attendu
