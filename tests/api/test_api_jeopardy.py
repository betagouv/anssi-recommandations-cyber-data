from fastapi.testclient import TestClient


def test_effectue_un_jeopardy_sur_une_collection(un_serveur_de_test_complet):
    (serveur, _, _, _, _) = un_serveur_de_test_complet(None)
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
    (serveur, _, _, _, service_jeopardy) = un_serveur_de_test_complet(None)
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
