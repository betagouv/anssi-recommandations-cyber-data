from fastapi.testclient import TestClient


def test_ajoute_un_document(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Indexation en cours d’exécution..."}


def test_appelle_le_service_d_indexation_de_documents(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf", "doc-2.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.appele
    assert service_indexation_document.documents_ajoutes == ["doc-1.pdf", "doc-2.pdf"]


def test_securise_la_route_documents(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
    )

    assert reponse.status_code == 401


def test_appelle_le_service_d_indexation_de_documents_pour_modifier_des_documents(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={
            "fichiers_ajoutes": ["doc-1.pdf", "doc-2.pdf"],
            "fichiers_modifies": ["doc-3.pdf"],
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.appele
    assert service_indexation_document.documents_ajoutes == [
        "doc-1.pdf",
        "doc-2.pdf",
        "doc-3.pdf",
    ]


def test_appelle_le_service_d_indexation_de_documents_pour_supprimer_des_documents(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={
            "fichiers_supprimes": ["doc-1.pdf", "doc-2.pdf"],
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.appele
    assert service_indexation_document.documents_supprimes == [
        "doc-1.pdf",
        "doc-2.pdf",
    ]


def test_ne_prends_que_les_fichiers_pdf_fournis_dans_la_requete(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={
            "fichiers_ajoutes": ["doc-1.pdf", "doc-2.avif"],
            "fichiers_modifies": ["doc-3.avif", "doc-4.pdf"],
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.documents_ajoutes == ["doc-1.pdf", "doc-4.pdf"]


def test_ne_prends_que_les_fichiers_pdf_fournis_dans_la_requete_pour_les_fichiers_a_supprimer(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={
            "fichiers_supprimes": ["doc-3.avif", "doc-4.pdf"],
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.documents_supprimes == [
        "doc-4.pdf",
    ]


def test_retourne_les_informations_des_documents_pour_la_collection_indexee(
    un_serveur_de_test_pour_collections,
):
    (serveur, *_) = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    reponse = client.get(
        "/api/documents/",
        params={"indexee": 3, "jeopardy": 1},
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    reponse_json = reponse.json()
    assert reponse_json["indexee"] == [
        {
            "id": "1",
            "nom": "doc-1.pdf",
            "date_de_creation": "2023-01-01T00:00:00",
            "chunks": 2,
        },
        {
            "id": "2",
            "nom": "doc-2.pdf",
            "date_de_creation": "2023-01-01T00:00:00",
            "chunks": 3,
        },
        {
            "id": "3",
            "nom": "doc-3.pdf",
            "date_de_creation": "2023-01-01T00:00:00",
            "chunks": 4,
        },
    ]


def test_retourne_les_informations_des_documents_pour_la_collection_jeopardy(
    un_serveur_de_test_pour_collections,
):
    (serveur, *_) = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    reponse = client.get(
        "/api/documents/",
        params={
            "indexee": 1,
            "jeopardy": 2,
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    reponse_json = reponse.json()
    assert reponse_json["jeopardy"] == [
        {
            "id": "1",
            "nom": "doc-1.pdf",
            "date_de_creation": "2023-01-01T00:00:00",
            "chunks": 2,
        },
        {
            "id": "2",
            "nom": "doc-2.pdf",
            "date_de_creation": "2023-01-01T00:00:00",
            "chunks": 3,
        },
    ]


def test_securise_la_route_GET_documents(un_serveur_de_test_pour_collections):
    (serveur, *_) = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    reponse = client.get(
        "/api/documents/",
        params={
            "indexee": 1,
            "jeopardy": 2,
        },
    )

    assert reponse.status_code == 401
