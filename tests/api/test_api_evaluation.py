import io
from pathlib import Path

from fastapi.testclient import TestClient


def les_fichiers_d_evaluation():
    fichier_evaluation = """col1,col2
Contenu col1,Contenu col2
"""

    fichiers_evaluation = {
        "fichier_evaluation": (
            "verite_terrain.csv",
            io.BytesIO(fichier_evaluation.encode()),
            "text/csv",
        ),
        "fichier_mapping": (
            "mapping.csv",
            io.BytesIO(fichier_evaluation.encode()),
            "text/csv",
        ),
    }
    return fichiers_evaluation


def test_lance_l_evaluation_d_une_collection(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
    )

    assert reponse.status_code == 200


def test_transmets_les_fichiers_d_evaluation(un_serveur_de_test_complet):
    (serveur, _, _, service_evaluation, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
    )

    assert service_evaluation.evaluation_lancee
    assert service_evaluation.chemin_fichier_evaluation == Path(
        "/tmp/verite_terrain.csv"
    )
    assert service_evaluation.chemin_fichier_mapping == Path("/tmp/mapping.csv")


def test_collecte_les_reponses_mqc_lors_d_une_evaluation(un_serveur_de_test_complet):
    (serveur, _, _, service_evaluation, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
    )

    assert service_evaluation.collecteur_de_reponse_appele
