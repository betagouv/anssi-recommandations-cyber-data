from jeopardy.service import ServiceJepoardy


def test_cree_une_collection(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = un_client_albert_de_test().avec_les_chunks_du_document(
        "doc-123",
        [
            {
                "id": 7,
                "content": "contenu source",
                "metadata": {"source": {"numero_page": 42}},
            }
        ],
    )

    ServiceJepoardy(
        client_albert, un_entrepot_memoire, "Un prompt", un_multiprocesseur
    ).jeopardyse(
        "Nom",
        "Description",
        "doc-123",
    )

    assert client_albert.collection_creee


def test_cree_une_collection_en_donnant_un_nom_et_une_description(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    client_albert = un_client_albert_de_test().avec_les_chunks_du_document(
        "doc-123",
        [
            {
                "id": 7,
                "content": "contenu source",
                "metadata": {"source": {"numero_page": 42}},
            }
        ],
    )

    ServiceJepoardy(
        client_albert, un_entrepot_memoire, "Prompt", un_multiprocesseur
    ).jeopardyse("Ma collection", "Ma description", "doc-123")

    assert client_albert.nom_collection_passe == "Jeopardy : Ma collection"
    assert client_albert.description_collection_passe == "Jeopardy : Ma description"


def test_recupere_les_chunks_du_document_source_depuis_son_identifiant(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    id_collection = "collection-123"
    id_document = "doc-source-123"

    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .qui_retourne_une_collection_avec_les_identifiants_de_document([id_document])
        .avec_les_chunks_du_document(
            id_document,
            [
                {
                    "id": 7,
                    "content": "contenu source",
                    "metadata": {"source": {"numero_page": 42}},
                }
            ],
        )
    )

    ServiceJepoardy(
        client_albert, un_entrepot_memoire, "Prompt", un_multiprocesseur
    ).jeopardyse(
        "Nom",
        "Description",
        id_collection,
    )

    assert client_albert.identifiant_document_lu == id_document


def test_ajoute_un_chunk_par_question_generee_dans_le_document_cree(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    id_collection = "collection-123"
    id_document = "doc-123"

    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .avec_un_identifiant_de_document_cree("doc-albert-456")
        .qui_retourne_une_collection_avec_les_identifiants_de_document([id_document])
        .avec_les_chunks_du_document(
            id_document,
            [
                {
                    "id": 7,
                    "content": "contenu source",
                    "metadata": {"source": {"numero_page": 42}},
                }
            ],
        )
        .qui_retourne_les_questions_generees(
            ["premiere question ?", "seconde question ?"]
        )
    )

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        un_multiprocesseur,
    ).jeopardyse(
        "Nom",
        "Description",
        id_collection,
    )

    appel = client_albert.appels_ajout_chunks[0]

    assert len(client_albert.appels_ajout_chunks) == 1
    assert len(appel.requete.chunks) == 2
    assert appel.identifiant_collection == "collection-123"
    assert appel.requete.id_document == "doc-albert-456"
    assert appel.requete.chunks[0]["content"] == "premiere question ?"
    assert appel.requete.chunks[1]["content"] == "seconde question ?"


def test_ajoute_les_metadonnees_utiles_dans_les_chunks_generes(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    id_collection = "collection-123"
    id_document = "doc-123"

    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .qui_retourne_une_collection_avec_les_identifiants_de_document([id_document])
        .avec_les_chunks_du_document(
            id_document,
            [
                {
                    "id": 99,
                    "content": "le contenu origine",
                    "metadata": {"page": 12},
                }
            ],
        )
        .qui_retourne_les_questions_generees(["question generee ?"])
    )

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        un_multiprocesseur,
    ).jeopardyse(
        "Nom",
        "Description",
        id_collection,
    )

    appel = client_albert.appels_ajout_chunks[0]
    chunk = appel.requete.chunks[0]

    assert chunk["content"] == "question generee ?"
    assert chunk["metadata"] == {
        "source_id_document": "doc-123",
        "source_id_chunk": 99,
        "source_numero_page": 12,
    }


def test_ajoute_les_chunks_de_questions_par_paquets_de_dix_en_utilisant_le_multiprocesseur(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    id_collection = "collection-123"
    id_document = "doc-123"

    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .qui_retourne_une_collection_avec_les_identifiants_de_document([id_document])
        .avec_les_chunks_du_document(
            id_document,
            [
                {
                    "id": i,
                    "content": f"le contenu numero {i}",
                    "metadata": {"source": {"numero_page": 42}},
                }
                for i in range(11)
            ],
        )
        .qui_retourne_les_questions_generees(["question unique ?"])
    )
    multi_processeur = un_multiprocesseur

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        multi_processeur,
    ).jeopardyse(
        "Nom",
        "Description",
        id_collection,
    )

    assert multi_processeur.a_ete_appele
    assert len(client_albert.appels_ajout_chunks) == 2
    assert len(client_albert.appels_ajout_chunks[0].requete.chunks) == 10
    assert len(client_albert.appels_ajout_chunks[1].requete.chunks) == 1


def test_recupere_les_chunks_depuis_albert_en_partant_de_la_collection(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
):
    id_collection = "collection-albert-42"
    identifiant_document = "doc-albert-42"
    client_albert = (
        un_client_albert_de_test()
        .avec_un_identifiant_de_collection(id_collection)
        .qui_retourne_une_collection_avec_les_identifiants_de_document(
            [identifiant_document]
        )
        .avec_les_chunks_du_document(
            identifiant_document,
            [
                {
                    "id": 7,
                    "content": "contenu depuis Albert",
                    "metadata": {"source": {"numero_page": 9}},
                }
            ],
        )
        .qui_retourne_les_questions_generees(["question depuis Albert ?"])
    )

    ServiceJepoardy(
        client_albert,
        un_entrepot_memoire,
        "Prompt",
        un_multiprocesseur,
    ).jeopardyse(
        "Nom",
        "Description",
        id_collection,
    )

    assert client_albert.identifiant_collection_lu == id_collection
    assert client_albert.identifiant_document_lu == identifiant_document
