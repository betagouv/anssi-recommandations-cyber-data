from jeopardy.collecteur import Chunk
from jeopardy.service import ServiceJepoardy


def test_cree_une_collection(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = un_client_albert_de_test()

    ServiceJepoardy(
        client_albert, un_entrepot_memoire, "Un prompt", un_multiprocesseur
    ).jeopardyse(
        "Nom",
        "Description",
        un_constructeur_de_document().construis(),
    )

    assert client_albert.collection_creee


def test_cree_une_collection_en_donnant_un_nom_et_une_description(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = un_client_albert_de_test()

    ServiceJepoardy(
        client_albert, un_entrepot_memoire, "Prompt", un_multiprocesseur
    ).jeopardyse(
        "Ma collection", "Ma description", un_constructeur_de_document().construis()
    )

    assert client_albert.nom_collection_passe == "Jeopardy : Ma collection"
    assert client_albert.description_collection_passe == "Jeopardy : Ma description"


def test_ajoute_un_document_a_la_collection(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = un_client_albert_de_test().avec_un_identifiant_de_collection(
        "collection-123"
    )

    ServiceJepoardy(
        client_albert, un_entrepot_memoire, "Prompt", un_multiprocesseur
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


def test_ajoute_un_chunk_par_question_generee_dans_le_document(
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
    document = (
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="contenu source", id=7, numero_page=42))
        .construis()
    )

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        un_multiprocesseur,
    ).jeopardyse(
        "Nom",
        "Description",
        document,
    )

    appel = client_albert.appels_ajout_chunks[0]

    assert len(client_albert.appels_ajout_chunks) == 1
    assert len(appel.requete.chunks) == 2
    assert appel.identifiant_collection == "collection-123"
    assert appel.requete.id_document == "doc-123"
    assert appel.requete.chunks[0]["contenu"] == "premiere question ?"
    assert appel.requete.chunks[1]["contenu"] == "seconde question ?"


def test_ajoute_les_metadonnees_utiles_dans_les_chunks_generes(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(["question generee ?"])
    )
    document = (
        un_constructeur_de_document()
        .ajoute_chunk(Chunk(contenu="le contenu origine", id=99, numero_page=12))
        .construis()
    )

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        un_multiprocesseur,
    ).jeopardyse(
        "Nom",
        "Description",
        document,
    )

    appel = client_albert.appels_ajout_chunks[0]
    chunk = appel.requete.chunks[0]

    assert chunk["contenu"] == "question generee ?"
    assert chunk["metadata"] == {
        "source": {
            "id_document": "doc-123",
            "id_chunk": 99,
            "numero_page": 12,
            "contenu_origine": "le contenu origine",
        }
    }


def test_ajoute_les_chunks_de_questions_par_paquets_de_dix_en_utilisant_le_multiprocesseur(
    un_constructeur_de_document,
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection("collection-123")
        .qui_retourne_les_questions_generees(["question unique ?"])
    )
    document = un_constructeur_de_document().ajoute_nombre_de_chunks(11).construis()
    multi_processeur = un_multiprocesseur

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        multi_processeur,
    ).jeopardyse(
        "Nom",
        "Description",
        document,
    )

    assert multi_processeur.a_ete_appele
    assert len(client_albert.appels_ajout_chunks) == 2
    assert len(client_albert.appels_ajout_chunks[0].requete.chunks) == 10
    assert len(client_albert.appels_ajout_chunks[1].requete.chunks) == 1
