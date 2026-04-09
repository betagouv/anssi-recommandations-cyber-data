from fastapi.testclient import TestClient


def test_effectue_un_jeopardy_sur_une_collection(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/jeopardy",
        json={
            "id_collection": "123",
            "nom_collection": "Nom",
            "description_collection": "Description",
        },
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Jeopardy en cours d’exécution..."}


def test_effectue_un_jeopardy_sur_une_collection_appelle_le_service(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, service_jeopardy, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/jeopardy",
        json={
            "id_collection": "123",
            "nom_collection": "Un jeopardy",
            "description_collection": "Description jeopardy",
        },
    )

    assert service_jeopardy.jeopardyse_appele
    assert service_jeopardy.identifiant_collection_a_jeopardyser == "123"
    assert service_jeopardy.nom_collection == "Un jeopardy"
    assert service_jeopardy.description_collection == "Description jeopardy"


def test_ajoute_des_documents_a_un_jeopardy_existant(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/jeopardy/12345/documents",
        json={
            "documents": ["doc-1", "doc-2"],
            "identifiant_collection": "0987",
        },
    )

    assert reponse.status_code == 200
    assert reponse.json() == {
        "message": "Ajout des documents de la collection 0987 dans la collection 12345 en cours d’exécution..."
    }


def test_effectue_un_jeopardy_sur_des_documents(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, service_jeopardy) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/jeopardy/12345/documents",
        json={
            "documents": ["doc-3", "doc-4", "doc-5"],
            "identifiant_collection": "0987",
        },
    )

    assert service_jeopardy.jeopardyse_documents_appele
    assert service_jeopardy.identifiant_collection_jeopardy == "12345"
    assert service_jeopardy.noms_documents_a_jeopardyser == ["doc-3", "doc-4", "doc-5"]
    assert service_jeopardy.identifiant_collection_a_jeopardyser == "0987"
