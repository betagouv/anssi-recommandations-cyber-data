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
    serveur, service = un_serveur_de_test_pour_collections()
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


def test_securise_la_route_collections(un_serveur_de_test_complet):
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

    # assert reponse.status_code == 200
    assert reponse.json() == {"message": "Indexation en cours d'exécution..."}
