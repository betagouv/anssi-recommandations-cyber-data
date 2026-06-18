from fastapi.testclient import TestClient


def test_finalise_retourne_les_details_de_l_erreur_422(
    un_serveur_de_test_pour_authentification,
):
    (serveur, _, _) = un_serveur_de_test_pour_authentification()
    client: TestClient = TestClient(serveur)

    # On envoie un payload avec un type incorrect pour un champ (challenge devrait être str)
    reponse = client.post(
        "/auth/finalise/",
        json={"credential": {}, "challenge": 123},
    )

    assert reponse.status_code == 422
    print(f"DEBUG RESPONSE: {reponse.json()}")
    details = reponse.json().get("detail")
    assert details is not None, (
        "Le payload de réponse devrait contenir un champ 'detail'"
    )
    assert len(details) > 0, "Le champ 'detail' ne devrait pas être vide"
    # Vérifier qu'on mentionne 'credential' ou 'challenge' qui sont manquants
    champs_manquants = [d.get("loc")[-1] for d in details]
    assert "credential" in champs_manquants or "challenge" in champs_manquants
