from fastapi.testclient import TestClient


def test_ajoute_un_document(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"message": "Indexation en cours d’exécution..."}
