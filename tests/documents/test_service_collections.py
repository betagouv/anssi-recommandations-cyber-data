from documents.service_collections import ServiceCollections, Collection


def test_recupere_les_collections_mqc(un_client_albert_collection):
    service = ServiceCollections(un_client_albert_collection)

    les_collections = service.les_collections()

    assert les_collections.indexee == Collection(
        id="1",
        nom="collection indexee",
        description="description",
        nombre_documents=1,
        date_de_creation="2026-04-23T15:39:27+00:00",
        date_de_derniere_modification="2026-04-23T15:39:37+00:00",
    )
    assert les_collections.jeopardy == Collection(
        id="2",
        nom="collection jeopardy",
        description="description jeopardy",
        nombre_documents=1,
        date_de_creation="2026-04-23T15:39:47+00:00",
        date_de_derniere_modification="2026-04-23T15:39:57+00:00",
    )
