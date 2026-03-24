from jeopardy.collecteur import CollecteurDeQuestions, Chunk


def test_cree_une_collection(un_client_albert_de_test):
    client_albert = un_client_albert_de_test()

    CollecteurDeQuestions(client_albert).collecte([])

    assert client_albert.collection_creee


def test_ajoute_un_document_a_la_collection(
    un_constructeur_de_document, un_client_albert_de_test
):
    client_albert = un_client_albert_de_test().avec_un_identifiant_de_collection(
        "collection-123"
    )

    CollecteurDeQuestions(client_albert).collecte(
        [un_constructeur_de_document().construis()]
    )

    assert client_albert.collection_attendue == "collection-123"
    assert client_albert.document_cree is not None
    assert client_albert.document_cree.metadata == {
        "source": {
            "nom_document": "Un document indexé",
            "id_document": "doc-123",
        }
    }


def test_recupere_les_questions(un_constructeur_de_document, un_client_albert_de_test):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )
    CollecteurDeQuestions(client_albert).collecte(
        [
            un_constructeur_de_document()
            .ajoute_chunk(Chunk(contenu="le contenu", id=0, numero_page=42))
            .construis(),
        ]
    )

    assert len(client_albert.questions_generees) == 2
    assert client_albert.questions_generees[0] == "premiere question ?"
    assert client_albert.questions_generees[1] == "seconde question ?"


def test_recupere_les_questions_pour_un_chunk_donne(
    un_constructeur_de_document, un_client_albert_de_test
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )
    CollecteurDeQuestions(client_albert).collecte(
        [
            un_constructeur_de_document()
            .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, numero_page=42))
            .ajoute_chunk(Chunk(contenu="le second contenu", id=1, numero_page=4))
            .construis(),
        ]
    )

    assert client_albert.chunks_fournis[0] == "le premier contenu"
    assert client_albert.chunks_fournis[1] == "le second contenu"
