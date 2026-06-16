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


def test_finalise_l_authentification(
    un_serveur_de_test_pour_authentification,
):
    (serveur, service_generation_challenge, _) = (
        un_serveur_de_test_pour_authentification()
    )
    client: TestClient = TestClient(serveur)
    credential = {
        "id": "456",
        "rawId": "456",
        "response": {
            "authenticatorData": "authenticator",
            "clientDataJSON": "clientData",
            "signature": "signature",
        },
        "type": "public-key",
        "clientExtensionResults": {},
    }

    reponse = client.post(
        "/auth/finalise/",
        json={"credential": credential, "challenge": "123"},
    )

    assert reponse.status_code == 200
    assert service_generation_challenge.credential_verifie == credential
    assert service_generation_challenge.challenge_attendu == "123"
    assert service_generation_challenge.rp_id_attendu == "localhost"
    assert service_generation_challenge.origine_attendue == "http://localhost"
    assert service_generation_challenge.verification_utilisateur_attendue


def test_finalise_l_authentification_en_fournissant_la_clef_publique_de_l_utilisateurice_reconnue(
    un_serveur_de_test_pour_authentification,
):
    (serveur, service_generation_challenge, _) = (
        un_serveur_de_test_pour_authentification()
    )
    client: TestClient = TestClient(serveur)
    credential = {
        "id": "456",
        "rawId": "456",
        "response": {
            "authenticatorData": "authenticator",
            "clientDataJSON": "clientData",
            "signature": "signature",
        },
        "type": "public-key",
        "clientExtensionResults": {},
    }

    reponse = client.post(
        "/auth/finalise/",
        json={"credential": credential, "challenge": "123"},
    )

    assert reponse.status_code == 200
    assert service_generation_challenge.clef_publique_attendue == "clef-publique-de-456"


def test_finalise_l_authentification_en_generant_un_token_jwt(
    un_serveur_de_test_pour_authentification,
):
    (serveur, service_generation_challenge, service_generation_token) = (
        un_serveur_de_test_pour_authentification()
    )
    client: TestClient = TestClient(serveur)
    credential = {
        "id": "456",
        "rawId": "456",
        "response": {
            "authenticatorData": "authenticator",
            "clientDataJSON": "clientData",
            "signature": "signature",
        },
        "type": "public-key",
        "clientExtensionResults": {},
    }

    client.post(
        "/auth/finalise/",
        json={"credential": credential, "challenge": "123"},
    )

    assert service_generation_token.token_genere


def test_finalise_l_authentification_en_ajoutant_le_token_dans_un_cookie(
    un_serveur_de_test_pour_authentification,
):
    (serveur, _, _) = un_serveur_de_test_pour_authentification()
    client: TestClient = TestClient(serveur)
    credential = {
        "id": "456",
        "rawId": "456",
        "response": {
            "authenticatorData": "authenticator",
            "clientDataJSON": "clientData",
            "signature": "signature",
        },
        "type": "public-key",
        "clientExtensionResults": {},
    }

    reponse = client.post(
        "/auth/finalise/",
        json={"credential": credential, "challenge": "123"},
    )

    assert "session" in reponse.cookies
    assert reponse.cookies["session"] == "token-genere"


def test_finalise_l_authentification_en_renvoyant_une_erreur_401_si_l_utilisateurice_est_inconnue(
    un_serveur_de_test_pour_authentification,
):
    (serveur, service_generation_challenge, _) = (
        un_serveur_de_test_pour_authentification()
    )
    client: TestClient = TestClient(serveur)
    credential = {
        "id": "789",
        "rawId": "789",
        "response": {
            "authenticatorData": "authenticator",
            "clientDataJSON": "clientData",
            "signature": "signature",
        },
        "type": "public-key",
        "clientExtensionResults": {},
    }

    reponse = client.post(
        "/auth/finalise/",
        json={"credential": credential, "challenge": "123"},
    )

    assert reponse.status_code == 401
