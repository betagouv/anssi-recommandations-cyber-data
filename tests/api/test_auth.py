from fastapi.testclient import TestClient


def test_initie_l_authentification(
    un_serveur_de_test_pour_authentification,
):
    (serveur, _, _) = un_serveur_de_test_pour_authentification()
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/auth/initie/",
        json={
            "utilisateur": "utilisateur.mqc",
        },
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"challenge": "123", "id": "456"}


def test_retourne_une_erreur_non_autorisee_si_l_utilisateurice_n_est_pas_connue(
    un_serveur_de_test_pour_authentification,
):
    (serveur, _, _) = un_serveur_de_test_pour_authentification()
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/auth/initie/",
        json={
            "utilisateur": "inconnu",
        },
    )

    assert reponse.status_code == 401
