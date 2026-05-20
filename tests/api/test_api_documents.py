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
