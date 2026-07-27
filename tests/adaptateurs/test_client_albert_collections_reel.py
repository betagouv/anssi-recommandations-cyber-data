import pytest
from adaptateurs.client_albert_collections_reel import ClientAlbertCollectionsReel
from adaptateurs.clients_albert import ReponseCollection, ReponseDocumentCollection
from configuration import CollectionsMQC


def test_utilise_l_id_de_collection_indexee_fourni_en_parametre(
    un_executeur_de_requete, une_reponse_de_recuperation_de_collection_OK
):
    reponse_indexee = ReponseCollection(
        id="1",
        name="collection indexée demandée",
        description="description",
        visibility="private",
        documents=1,
        created="1672531200",
        updated="1672531200",
    )
    reponse_jeopardy = ReponseCollection(
        id="2",
        name="collection jeopardy",
        description="description",
        visibility="private",
        documents=1,
        created="1672531200",
        updated="1672531200",
    )
    client = ClientAlbertCollectionsReel(
        "https://test.api",
        "test-key",
        CollectionsMQC(id_collection_indexee="1", id_collection_jeopardy="2"),
        un_executeur_de_requete(
            [
                une_reponse_de_recuperation_de_collection_OK(reponse_indexee),
                une_reponse_de_recuperation_de_collection_OK(reponse_jeopardy),
            ]
        ),
    )

    resultat = client.recupere_collections_mqc(id_collection_indexee="1")

    assert resultat[0].id == "1"


def test_utilise_l_id_de_collection_jeopardy_fourni_en_parametre(
    un_executeur_de_requete, une_reponse_de_recuperation_de_collection_OK
):
    reponse_indexee = ReponseCollection(
        id="1",
        name="collection indexee",
        description="description",
        visibility="private",
        documents=1,
        created="1672531200",
        updated="1672531200",
    )
    reponse_jeopardy = ReponseCollection(
        id="2",
        name="collection jeopardy demandée",
        description="description",
        visibility="private",
        documents=1,
        created="1672531200",
        updated="1672531200",
    )
    client = ClientAlbertCollectionsReel(
        "https://test.api",
        "test-key",
        CollectionsMQC(id_collection_indexee="1", id_collection_jeopardy="2"),
        un_executeur_de_requete(
            [
                une_reponse_de_recuperation_de_collection_OK(reponse_indexee),
                une_reponse_de_recuperation_de_collection_OK(reponse_jeopardy),
            ]
        ),
    )

    resultat = client.recupere_collections_mqc(id_collection_jeopardy="2")

    assert resultat[1].id == "2"


def test_utilise_les_ids_configures_quand_aucun_id_n_est_fourni(
    un_executeur_de_requete, une_reponse_de_recuperation_de_collection_OK
):
    reponse_indexee = ReponseCollection(
        id="1",
        name="collection indexee",
        description="description",
        visibility="private",
        documents=1,
        created="1672531200",
        updated="1672531200",
    )
    reponse_jeopardy = ReponseCollection(
        id="2",
        name="collection jeopardy",
        description="description",
        visibility="private",
        documents=1,
        created="1672531200",
        updated="1672531200",
    )
    client = ClientAlbertCollectionsReel(
        "https://test.api",
        "test-key",
        CollectionsMQC(id_collection_indexee="1", id_collection_jeopardy="2"),
        un_executeur_de_requete(
            [
                une_reponse_de_recuperation_de_collection_OK(reponse_indexee),
                une_reponse_de_recuperation_de_collection_OK(reponse_jeopardy),
            ]
        ),
    )

    resultat = client.recupere_collections_mqc()

    assert resultat[0].id == "1"
    assert resultat[1].id == "2"


@pytest.mark.parametrize(
    "kwargs_id, id_attendu",
    [
        ({"id_collection_indexee": "42"}, "42"),
        ({}, "1"),
    ],
)
def test_l_id_de_collection_indexee_utilise_pour_les_documents(
    un_executeur_de_requete, une_reponse_de_liste_collections_OK, kwargs_id, id_attendu
):
    documents = [
        ReponseDocumentCollection(
            id="1", name="doc-1.pdf", created="1672531200", chunks=2
        )
    ]
    executeur = un_executeur_de_requete([une_reponse_de_liste_collections_OK(documents)])
    client = ClientAlbertCollectionsReel(
        "https://test.api",
        "test-key",
        CollectionsMQC(id_collection_indexee="1", id_collection_jeopardy="2"),
        executeur,
    )

    client.recupere_documents_collection(
        offset_indexation=1, offset_jeopardy=0, **kwargs_id
    )

    assert (
        executeur.parametres_recus["https://test.api/documents"]["collection_id"]
        == id_attendu
    )


@pytest.mark.parametrize(
    "kwargs_id, id_attendu",
    [
        ({"id_collection_jeopardy": "43"}, "43"),
        ({}, "2"),
    ],
)
def test_l_id_de_collection_jeopardy_utilise_pour_les_documents(
    un_executeur_de_requete, une_reponse_de_liste_collections_OK, kwargs_id, id_attendu
):
    documents = [
        ReponseDocumentCollection(
            id="1", name="doc-1.pdf", created="1672531200", chunks=2
        )
    ]
    executeur = un_executeur_de_requete([une_reponse_de_liste_collections_OK(documents)])
    client = ClientAlbertCollectionsReel(
        "https://test.api",
        "test-key",
        CollectionsMQC(id_collection_indexee="1", id_collection_jeopardy="2"),
        executeur,
    )

    client.recupere_documents_collection(
        offset_indexation=0, offset_jeopardy=1, **kwargs_id
    )

    assert (
        executeur.parametres_recus["https://test.api/documents"]["collection_id"]
        == id_attendu
    )


def test_liste_les_collections_disponibles_avec_les_bons_parametres(
    un_executeur_de_requete, une_reponse_de_liste_collections_OK
):
    collections_disponibles = [
        ReponseCollection(
            id="1",
            name="collection A",
            description="description",
            visibility="private",
            documents=1,
            created="1672531200",
            updated="1672531200",
        ),
        ReponseCollection(
            id="2",
            name="collection B",
            description="description",
            visibility="private",
            documents=2,
            created="1672531300",
            updated="1672531300",
        ),
    ]
    executeur = un_executeur_de_requete(
        [une_reponse_de_liste_collections_OK(collections_disponibles)]
    )
    client = ClientAlbertCollectionsReel(
        "https://test.api",
        "test-key",
        CollectionsMQC(id_collection_indexee="1", id_collection_jeopardy="2"),
        executeur,
    )

    resultat = client.liste_les_collections_disponibles()

    assert executeur.parametres_recus["https://test.api/collections"] == {
        "limit": 10,
        "order_by": "created",
        "order_direction": "desc",
        "visibility": "private",
    }
    assert [c.id for c in resultat] == ["1", "2"]