import json

from fastapi.testclient import TestClient


def test_initie_l_enrolement_de_la_clef(
    un_serveur_de_test_pour_authentification,
):
    (serveur, service_authentification, _) = un_serveur_de_test_pour_authentification()

    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/auth/enrole/",
        json={
            "utilisateur": "jean.dujardin",
        },
    )

    assert reponse.status_code == 200
    reponse_json = reponse.json()
    assert json.loads(reponse_json["options"]) == {
        "rp": {"name": "Tableau de bord admin MQC data", "id": "localhost"},
        "user": {"id": "MQ", "name": "jean.dujardin", "displayName": "jean.dujardin"},
        "challenge": "MTIz",
        "pubKeyCredParams": [
            {"type": "public-key", "alg": -7},
            {"type": "public-key", "alg": -8},
        ],
        "excludeCredentials": [],
        "authenticatorSelection": {
            "residentKey": "required",
            "requireResidentKey": True,
            "userVerification": "required",
        },
        "attestation": "none",
    }
    assert service_authentification.challenge_enrolement_persiste


def test_verifie_l_enrolement(un_serveur_de_test_pour_authentification):
    (serveur, service_authentification, _) = un_serveur_de_test_pour_authentification()

    client: TestClient = TestClient(serveur)
    reponse = client.post(
        "/auth/verifie-enrolement/",
        json={
            "credential": {
                "id": "123",
                "rawId": "456",
                "response": {
                    "attestationObject": "attestation",
                    "clientDataJSON": "client",
                },
            },
            "utilisateur": "jean.dujardin",
        },
    )
    assert reponse.status_code == 200
    assert reponse.json
    assert service_authentification.verification_enrolement_credential == {
        "id": "123",
        "rawId": "456",
        "response": {"attestationObject": "attestation", "clientDataJSON": "client"},
    }
    assert service_authentification.verification_enrolement_challenge == "789"


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
            "userHandle": None,
        },
        "type": "public-key",
    }

    reponse = client.post(
        "/auth/finalise/",
        json={"credential": credential, "utilisateur": "jeanne.dupont"},
    )

    assert reponse.status_code == 200
    assert service_generation_challenge.credential_verifie == credential
    assert service_generation_challenge.challenge_attendu == "789"
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
        json={"credential": credential, "utilisateur": "jeanne.dupont"},
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
        json={"credential": credential, "utilisateur": "jeanne.dupont"},
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
        json={"credential": credential, "utilisateur": "jeanne.dupont"},
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
        json={"credential": credential, "utilisateur": "jeanne.dupont"},
    )

    assert reponse.status_code == 401
