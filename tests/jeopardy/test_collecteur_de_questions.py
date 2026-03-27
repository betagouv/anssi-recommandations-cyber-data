from jeopardy.collecteur import CollecteurDeQuestions, Chunk
from jeopardy.questions import EntrepotQuestionGenereeMemoire

PROMPT = "Prompt"
NOM_COLLECTION = "Collection"
DESCRIPTION_COLLECTION = "Description"


def test_recupere_les_questions(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    CollecteurDeQuestions(
        client_albert, "Prompt", un_entrepot_memoire, un_multiprocesseur
    ).collecte(
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le contenu", id=0, numero_page=42))
        .construis(),
    )

    assert len(client_albert.questions_generees) == 2
    assert client_albert.questions_generees[0] == "premiere question ?"
    assert client_albert.questions_generees[1] == "seconde question ?"


def test_recupere_les_questions_pour_un_chunk_donne(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    CollecteurDeQuestions(
        client_albert, "Prompt", un_entrepot_memoire, un_multiprocesseur
    ).collecte(
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, numero_page=42))
        .ajoute_chunk(Chunk(contenu="le second contenu", id=1, numero_page=4))
        .construis(),
    )

    assert client_albert.chunks_fournis[0] == "le premier contenu"
    assert client_albert.chunks_fournis[1] == "le second contenu"


def test_verifie_qu_on_passe_un_prompt_a_notre_generateur_de_questions(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    CollecteurDeQuestions(
        client_albert, "mon prompt", un_entrepot_memoire, un_multiprocesseur
    ).collecte(
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, numero_page=42))
        .construis(),
    )

    assert client_albert.prompt_passe == "mon prompt"


def test_persiste_les_questions_generees(
    un_constructeur_de_document, un_client_albert_de_test, un_multiprocesseur
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )
    document = (
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, numero_page=42))
        .construis()
    )
    entrepot_questions_generees = EntrepotQuestionGenereeMemoire()

    CollecteurDeQuestions(
        client_albert, "Prompt", entrepot_questions_generees, un_multiprocesseur
    ).collecte(document)

    toutes_les_questions = entrepot_questions_generees.tous()
    assert len(toutes_les_questions) == 2
    assert toutes_les_questions[0].contenu == "premiere question ?"
    assert toutes_les_questions[0].contenu_origine == "le premier contenu"
    assert toutes_les_questions[0].id_document == document.id_document
    assert toutes_les_questions[0].id_chunk == 0
    assert toutes_les_questions[0].numero_page == 42
    assert toutes_les_questions[1].contenu == "seconde question ?"
    assert toutes_les_questions[0].contenu_origine == "le premier contenu"
    assert toutes_les_questions[1].id_document == document.id_document
    assert toutes_les_questions[1].id_chunk == 0
    assert toutes_les_questions[1].numero_page == 42


def test_traite_les_chunks_en_parallele(
    un_constructeur_de_document, un_client_albert_de_test, un_multiprocesseur
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )
    document = un_constructeur_de_document().ajoute_nombre_de_chunks(11).construis()
    entrepot_questions_generees = EntrepotQuestionGenereeMemoire()
    multi_processeur = un_multiprocesseur

    CollecteurDeQuestions(
        client_albert, "Prompt", entrepot_questions_generees, multi_processeur
    ).collecte(document)

    assert multi_processeur.a_ete_appele
