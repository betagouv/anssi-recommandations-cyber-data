import io

from fastapi.testclient import TestClient

from infra.memoire.executeur_de_requete_memoire import ReponseTexteEnSucces, TypeRequete


def toto():
    questions = """question_originale,reformulation_ideale
Qu'est-ce qu'une attaque DDOS ?,Qu'est-ce qu'une attaque DDOS (attaque par déni de service distribué) ?
"""

    fichier_questions = {
        "file": ("test.csv", io.BytesIO(questions.encode()), "text/csv")
    }
    return fichier_questions


def test_lance_une_evaluation_de_reformulation_retourne_201(un_serveur_de_test_complet):
    (serveur, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/evaluation/reformulation",
        data={"url_prompt": "https://une-url.com"},
        files=toto(),
    )

    assert reponse.status_code == 201
    contenu_reponse = reponse.json()
    assert contenu_reponse["id"] is not None
    assert contenu_reponse["nombre_questions"] == 1


def test_lance_une_evaluation_de_reformulation_avec_les_questions_fournies(
    un_serveur_de_test_complet,
):
    (serveur, _, _, service_evaluation) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/evaluation/reformulation",
        data={"url_prompt": "https://une-url.com"},
        files=toto(),
    )

    assert service_evaluation.evaluation_reformulation_lancee
    assert len(service_evaluation.questions_evaluees) == 1


def test_lance_une_evaluation_de_reformulation_avec_le_prompt_attendu(
    un_serveur_de_test_complet, un_executeur_de_requete, une_reponse_attendue_OK
):
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(
                ReponseTexteEnSucces(texte="Prompt attendu"), TypeRequete.GET
            )
        ]
    )
    (serveur, _, _, service_evaluation) = un_serveur_de_test_complet(
        executeur_de_requete
    )
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/evaluation/reformulation",
        data={"url_prompt": "https://une-url.com"},
        files=toto(),
    )

    assert executeur_de_requete.url_appelee == "https://une-url.com/"
    assert service_evaluation.prompt_recu == "Prompt attendu"
