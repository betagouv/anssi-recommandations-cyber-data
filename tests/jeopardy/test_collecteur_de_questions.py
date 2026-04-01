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
    un_bus_d_evenement,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    CollecteurDeQuestions(
        client_albert,
        "Prompt",
        un_entrepot_memoire,
        un_bus_d_evenement,
        un_multiprocesseur,
    ).collecte(
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le contenu", id=0, page=42))
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
    un_bus_d_evenement,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    CollecteurDeQuestions(
        client_albert,
        "Prompt",
        un_entrepot_memoire,
        un_bus_d_evenement,
        un_multiprocesseur,
    ).collecte(
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, page=42))
        .ajoute_chunk(Chunk(contenu="le second contenu", id=1, page=4))
        .construis(),
    )

    assert client_albert.chunks_fournis[0] == "le premier contenu"
    assert client_albert.chunks_fournis[1] == "le second contenu"


def test_verifie_qu_on_passe_un_prompt_a_notre_generateur_de_questions(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
    un_bus_d_evenement,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    CollecteurDeQuestions(
        client_albert,
        "mon prompt",
        un_entrepot_memoire,
        un_bus_d_evenement,
        un_multiprocesseur,
    ).collecte(
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, page=42))
        .construis(),
    )

    assert client_albert.prompt_passe == "mon prompt"


def test_persiste_les_questions_generees(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_multiprocesseur,
    un_bus_d_evenement,
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
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, page=42))
        .construis()
    )
    entrepot_questions_generees = EntrepotQuestionGenereeMemoire()

    CollecteurDeQuestions(
        client_albert,
        "Prompt",
        entrepot_questions_generees,
        un_bus_d_evenement,
        un_multiprocesseur,
    ).collecte(document)

    toutes_les_questions = entrepot_questions_generees.tous()
    assert len(toutes_les_questions) == 2
    assert toutes_les_questions[0].contenu == "premiere question ?"
    assert toutes_les_questions[0].contenu_origine == "le premier contenu"
    assert toutes_les_questions[0].id_document == document.id_document
    assert toutes_les_questions[0].id_chunk == 0
    assert toutes_les_questions[0].page == 42
    assert toutes_les_questions[1].contenu == "seconde question ?"
    assert toutes_les_questions[0].contenu_origine == "le premier contenu"
    assert toutes_les_questions[1].id_document == document.id_document
    assert toutes_les_questions[1].id_chunk == 0
    assert toutes_les_questions[1].page == 42


def test_traite_les_chunks_en_parallele(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_multiprocesseur,
    un_bus_d_evenement,
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
        client_albert,
        "Prompt",
        entrepot_questions_generees,
        un_bus_d_evenement,
        multi_processeur,
    ).collecte(document)

    assert multi_processeur.a_ete_appele


def test_stoppe_l_ajout_de_tous_les_chunks_si_une_erreur_est_levee(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_multiprocesseur,
    un_bus_d_evenement,
):
    id_collection = "collection-123"
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .levant_une_erreur_sur_la_generation_de_question_pour_le_chunk(
            "CONTENU_EN_ERREUR"
        )
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )
    entrepot_questions_generees = EntrepotQuestionGenereeMemoire()
    document = (
        un_constructeur_de_document()
        .ajoute_nombre_de_chunks(10)
        .ajoute_chunk(Chunk(id=10, contenu="CONTENU_EN_ERREUR", page=10))
        .construis()
    )

    CollecteurDeQuestions(
        client_albert,
        "Prompt",
        entrepot_questions_generees,
        un_bus_d_evenement,
        un_multiprocesseur,
    ).collecte(document)

    assert len(entrepot_questions_generees.tous()) == 0


def test_publie_sur_le_bus_d_evenement_lorsqu_une_erreur_est_levee(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_multiprocesseur,
    un_bus_d_evenement,
):
    id_collection = "collection-123"
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .levant_une_erreur_sur_la_generation_de_question_pour_le_chunk(
            "CONTENU_EN_ERREUR"
        )
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )
    entrepot_questions_generees = EntrepotQuestionGenereeMemoire()
    document = (
        un_constructeur_de_document()
        .ajoute_nombre_de_chunks(10)
        .ajoute_chunk(Chunk(id=10, contenu="CONTENU_EN_ERREUR", page=10))
        .construis()
    )

    bus_d_evenement = un_bus_d_evenement
    CollecteurDeQuestions(
        client_albert,
        "Prompt",
        entrepot_questions_generees,
        bus_d_evenement,
        un_multiprocesseur,
    ).collecte(document)

    assert len(bus_d_evenement.evenements) == 1
    assert bus_d_evenement.evenements[0].type == "QUESTIONS_GENEREES_EN_ERREUR"
    assert (
        bus_d_evenement.evenements[0].corps.erreur
        == "Erreur lors de la génération de questions"
    )


def test_publie_sur_le_bus_d_evenement_les_questions_generees(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_multiprocesseur,
    un_bus_d_evenement,
):
    questions_generees = ["premiere question ?", "seconde question ?"]
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(questions_generees)
    )
    document = (
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le premier contenu", id=0, page=42))
        .construis()
    )
    entrepot_questions_generees = EntrepotQuestionGenereeMemoire()

    bus_d_evenement = un_bus_d_evenement
    CollecteurDeQuestions(
        client_albert,
        "Prompt",
        entrepot_questions_generees,
        bus_d_evenement,
        un_multiprocesseur,
    ).collecte(document)

    assert len(bus_d_evenement.evenements) == 1
    assert bus_d_evenement.evenements[0].type == "QUESTIONS_GENEREES"
    assert len(bus_d_evenement.evenements[0].corps.questions_generees) == len(
        questions_generees
    )
    assert bus_d_evenement.evenements[0].corps.id_document == document.id_document
    assert bus_d_evenement.evenements[0].corps.nombre_chunks_origine == 1
