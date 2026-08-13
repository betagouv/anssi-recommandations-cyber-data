from fastapi.testclient import TestClient

from documents.indexeur.indexeur import (
    ReponseDocumentEnErreur,
    ReponseDocumentIndexePartiellement,
)


def test_ajoute_un_document(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    contenu = reponse.json()
    assert contenu["message"] == "Indexation en cours d’exécution..."
    assert contenu["identifiant_operation"]


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


def test_transmet_l_identifiant_de_la_collection_source_selectionnee(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={
            "fichiers_ajoutes": ["doc-1.pdf"],
            "id_collection_indexee": "collection-selectionnee",
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.id_collection_indexee == "collection-selectionnee"


def test_transmet_l_url_du_document_a_ajouter_au_service_d_indexation(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = un_serveur_de_test_complet(
        None
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/documents/",
        json={"url_a_ajouter": "https://cyber.gouv.fr/cyberdico/"},
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_indexation_document.appele
    assert service_indexation_document.url_a_ajouter == "https://cyber.gouv.fr/cyberdico/"


def test_securise_la_route_documents(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
    )

    assert reponse.status_code == 401


def test_retourne_un_identifiant_de_suivi_de_l_indexation(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.json()["identifiant_operation"]


def test_retourne_le_statut_termine_sans_erreur(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )
    identifiant_operation = reponse.json()["identifiant_operation"]

    statut = client.get(
        f"/api/documents/indexation/{identifiant_operation}",
        headers={"Authorization": "Bearer token-valide"},
    )

    assert statut.json() == {
        "statut": "terminee",
        "erreurs": [],
        "documents_partiels": [],
    }


def test_retourne_le_statut_en_erreur_avec_le_document_et_le_detail(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, service_indexation_document) = (
        un_serveur_de_test_complet(None)
    )
    service_indexation_document.resultats_indexation = [
        ReponseDocumentEnErreur(
            detail="ReadTimeout après 300 secondes",
            document_en_erreur="doc-1.pdf",
        )
    ]
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )
    identifiant_operation = reponse.json()["identifiant_operation"]

    statut = client.get(
        f"/api/documents/indexation/{identifiant_operation}",
        headers={"Authorization": "Bearer token-valide"},
    )

    assert statut.json() == {
        "statut": "terminee_avec_erreurs",
        "erreurs": [
            {
                "document": "doc-1.pdf",
                "detail": "ReadTimeout après 300 secondes",
            }
        ],
        "documents_partiels": [],
    }


def test_retourne_le_statut_partiel_et_les_pages_non_indexees(
    un_serveur_de_test_complet,
) -> None:
    (serveur, _, _, _, _, _, service_indexation_document) = (
        un_serveur_de_test_complet(None)
    )
    service_indexation_document.resultats_indexation = [
        ReponseDocumentIndexePartiellement(
            id="doc-1",
            nom="doc-1.pdf",
            id_collection="123",
            date_creation="",
            date_mise_a_jour="",
            pages_non_indexees=(18,),
            erreurs=("Réponse JSON invalide",),
        )
    ]
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/documents/",
        json={"fichiers_ajoutes": ["doc-1.pdf"]},
        headers={"Authorization": "Bearer token-valide"},
    )
    identifiant_operation = reponse.json()["identifiant_operation"]

    statut = client.get(
        f"/api/documents/indexation/{identifiant_operation}",
        headers={"Authorization": "Bearer token-valide"},
    )

    assert statut.json() == {
        "statut": "terminee_partiellement",
        "erreurs": [],
        "documents_partiels": [
            {
                "document": "doc-1.pdf",
                "id": "doc-1",
                "pages_non_indexees": [18],
                "erreurs": ["Réponse JSON invalide"],
            }
        ],
    }


def test_retourne_une_erreur_pour_un_identifiant_de_suivi_inconnu(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.get(
        "/api/documents/indexation/inconnu",
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 404


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


def test_transmet_les_ids_de_collection_a_la_route_documents(
    un_serveur_de_test_pour_collections,
):
    (serveur, _, service_collections) = un_serveur_de_test_pour_collections()
    client: TestClient = TestClient(serveur)

    client.get(
        "/api/documents/",
        params={
            "indexee": 1,
            "jeopardy": 1,
            "id_collection_indexee": "42",
            "id_collection_jeopardy": "43",
        },
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_collections.ids_recus_documents == ("42", "43")


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
