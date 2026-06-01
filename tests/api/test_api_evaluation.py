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


def les_fichiers_d_evaluation_path_traversal_pour_le_fichier_d_evaluation():
    fichier_evaluation = """col1,col2
Contenu col1,Contenu col2
"""
    chemin_fichier_evaluation = Path("/tmp/path_traversal.py")
    chemin_fichier_evaluation.touch()
    chemin_fichier_evaluation.write_text('var = "CONTENU ORIGINAL"')
    # chemin_fichier_evaluation = join("../Users/bertrand/ajairu/beta-gouv/mqc/anssi-recommandations-cyber-data/tests/api/path_traversal.py")
    fichiers_evaluation = {
        "fichier_evaluation": (
            "../tmp/path_traversal.py",
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


def les_fichiers_d_evaluation_path_traversal_pour_le_mapping():
    fichier_evaluation = """col1,col2
Contenu col1,Contenu col2
"""
    chemin_fichier_mapping = Path("/tmp/path_traversal_mapping.py")
    chemin_fichier_mapping.touch()
    chemin_fichier_mapping.write_text('var = "CONTENU ORIGINAL"')
    fichiers_evaluation = {
        "fichier_evaluation": (
            "verite_terrain.csv",
            io.BytesIO(fichier_evaluation.encode()),
            "text/csv",
        ),
        "fichier_mapping": (
            "../tmp/path_traversal_mapping.py",
            io.BytesIO(fichier_evaluation.encode()),
            "text/csv",
        ),
    }
    return fichiers_evaluation


def test_lance_l_evaluation_d_une_collection(un_serveur_de_test_complet):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200


def test_transmets_les_fichiers_d_evaluation(un_serveur_de_test_complet):
    (serveur, _, _, service_evaluation, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_evaluation.evaluation_lancee
    assert service_evaluation.chemin_fichier_evaluation.name == "verite_terrain.csv"
    assert service_evaluation.chemin_fichier_mapping.name == "mapping.csv"


def test_retourne_401_si_aucun_token_transmis(un_serveur_de_test_complet):
    (serveur, *_) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
    )

    assert reponse.status_code == 401


def test_collecte_les_reponses_mqc_lors_d_une_evaluation(un_serveur_de_test_complet):
    (serveur, _, _, service_evaluation, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation(),
        headers={"Authorization": "Bearer token-valide"},
    )

    assert service_evaluation.collecteur_de_reponse_appele


def test_lance_l_evaluation_d_une_collection_sans_ecraser_le_contenu_d_un_fichier_existant(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation_path_traversal_pour_le_fichier_d_evaluation(),
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    assert Path("/tmp/path_traversal.py").read_text() == 'var = "CONTENU ORIGINAL"'


def test_lance_l_evaluation_d_une_collection_sans_ecraser_le_contenu_d_un_fichier_existant_avec_ɇ_āpping(
    un_serveur_de_test_complet,
):
    (serveur, _, _, _, _, _, _) = un_serveur_de_test_complet(None)
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/evaluation",
        files=les_fichiers_d_evaluation_path_traversal_pour_le_mapping(),
        headers={"Authorization": "Bearer token-valide"},
    )

    assert reponse.status_code == 200
    assert (
        Path("/tmp/path_traversal_mapping.py").read_text() == 'var = "CONTENU ORIGINAL"'
    )
