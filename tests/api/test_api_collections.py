from fastapi.testclient import TestClient

import jwt


def test_cree_une_nouvelle_collection(un_serveur_de_test_complet):
    (serveur, *_) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/collections/",
        json={
            "nom": "ma-collection",
            "description": "une description",
            "fichiers": ["doc-1.pdf"],
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Indexation en cours d'exécution..."}


def test_appelle_le_service_indexation_collections(un_serveur_de_test_pour_collections):
    serveur, service, _ = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/collections/",
        json={
            "nom": "ma-collection",
            "description": "une description",
            "fichiers": ["doc-1.pdf", "doc-2.pdf"],
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service.appele
    assert service.nom == "ma-collection"
    assert service.description == "une description"
    assert service.sources.fichiers == ["doc-1.pdf", "doc-2.pdf"]


def test_securise_la_route_POST_collections(un_serveur_de_test_complet):
    (serveur, *_) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/collections/",
        json={
            "nom": "ma-collection",
            "description": "une description",
            "fichiers": ["doc-1.pdf"],
        },
    )

    assert reponse.status_code == 401


def test_valide_le_token_jwt_dans_un_cookie_de_session(un_serveur_de_test_complet):
    (serveur, *_) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)
    token_valide = jwt.encode({"some": "payload"}, "SECRET", algorithm="HS256")

    reponse = client.post(
        "/api/collections/",
        json={
            "nom": "ma-collection",
            "description": "une description",
            "fichiers": ["doc-1.pdf"],
        },
        cookies={"session": token_valide},
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Indexation en cours d'exécution..."}


def test_recupere_la_collection_d_indexation(un_serveur_de_test_pour_collections):
    (serveur, *_) = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    reponse = client.get(
        "/api/collections/",
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    assert reponse.json() == {
        "indexee": {
            "id": "1",
            "nom": "Une collection",
            "description": "une description",
            "date_de_creation": "2026-06-12T12:47:00",
            "date_de_derniere_modification": "2026-06-12T15:52:00",
            "nombre_documents": 1,
        },
        "jeopardy": {
            "id": "2",
            "nom": "Une collection Jeopardy",
            "description": "une description jeopardy",
            "date_de_creation": "2026-06-12T12:48:00",
            "date_de_derniere_modification": "2026-06-12T15:53:00",
            "nombre_documents": 1,
        },
    }


def test_securise_la_route_GET_collections(un_serveur_de_test_pour_collections):
    (serveur, *_) = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    reponse = client.get(
        "/api/collections/",
    )

    assert reponse.status_code == 401
