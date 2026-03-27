from jeopardy.service import ServiceJepoardy


def test_cree_une_collection(
        un_constructeur_de_document, un_client_albert_de_test, un_entrepot_memoire, un_multiprocesseur
):
    client_albert = un_client_albert_de_test()

    ServiceJepoardy(
        client_albert,  un_entrepot_memoire,"Un prompt", un_multiprocesseur
    ).jeopardyse(
        "Nom",
        "Description",
        un_constructeur_de_document().construis(),
    )

    assert client_albert.collection_creee


def test_cree_une_collection_en_donnant_un_nom_et_une_description(
        un_constructeur_de_document, un_client_albert_de_test, un_entrepot_memoire, un_multiprocesseur
):
    client_albert = un_client_albert_de_test()

    ServiceJepoardy(
        client_albert,  un_entrepot_memoire, "Prompt", un_multiprocesseur
    ).jeopardyse(
        "Ma collection", "Ma description", un_constructeur_de_document().construis()
    )

    assert client_albert.nom_collection_passe == "Jeopardy : Ma collection"
    assert client_albert.description_collection_passe == "Jeopardy : Ma description"


def test_ajoute_un_document_a_la_collection(
        un_constructeur_de_document, un_client_albert_de_test, un_entrepot_memoire, un_multiprocesseur
):
    client_albert = un_client_albert_de_test().avec_un_identifiant_de_collection(
        "collection-123"
    )

    ServiceJepoardy(
        client_albert,  un_entrepot_memoire,"Prompt", un_multiprocesseur
    ).jeopardyse(
        "Nom",
        "Description",
        un_constructeur_de_document().construis(),
    )

    assert client_albert.collection_attendue == "collection-123"
    assert client_albert.document_cree is not None
    assert client_albert.document_cree.metadata == {
        "source": {
            "nom_document": "Un document indexé",
            "id_document": "doc-123",
        }
    }