from pathlib import Path
import pandas as pd
import httpx
import respx
import pytest

from src.configuration import recupere_configuration, MQC
from src.remplisseur_reponses import (
    RemplisseurReponses,
    EcrivainSortie,
    ClientMQCHTTP,
    HorlogeSysteme,
    construit_base_url,
    formate_route_pose_question,
)


@pytest.fixture()
def configuration() -> MQC:
    return recupere_configuration()


@respx.mock
def test_remplissage_appelle_api_pour_chaque_question(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    route = respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json={"reponse": "X"})
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    remplisseur.remplit_fichier(fichier)

    assert route.called
    assert route.call_count == 2


@respx.mock
def test_remplissage_insere_reponses_dans_colonne(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json={"reponse": "mocked"})
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = remplisseur.remplit_fichier(fichier)
    df: pd.DataFrame = lecteur.dataframe

    assert list(df["Réponse Bot"]) == ["mocked", "mocked"]


@respx.mock
def test_ecriture_cree_fichier_dans_bon_dossier(tmp_path: Path, configuration: MQC):
    (tmp_path / "donnees" / "sortie").mkdir(parents=True, exist_ok=True)
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json={"reponse": "OK"})
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = remplisseur.remplit_fichier(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_fichier_depuis_lecteur_csv(
        lecteur, prefixe="evaluation"
    )

    assert chemin_csv.parent == tmp_path / "donnees" / "sortie"


@respx.mock
def test_ecriture_nom_fichier_contient_date(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json={"reponse": "OK"})
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = remplisseur.remplit_fichier(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_fichier_depuis_lecteur_csv(
        lecteur, prefixe="evaluation"
    )

    assert "evaluation_" in chemin_csv.name


@respx.mock
def test_ecriture_contenu_csv_complet(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\nB?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json={"reponse": "OK"})
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = remplisseur.remplit_fichier(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_fichier_depuis_lecteur_csv(
        lecteur, prefixe="evaluation"
    )

    contenu = chemin_csv.read_text(encoding="utf-8").splitlines()
    assert contenu[0].startswith("Question type")
    assert "A?,OK" in contenu[1]
    assert "B?,OK" in contenu[2]


def test_pose_question_declenche_exception_si_serveur_injoignable(configuration):
    client = ClientMQCHTTP(cfg=configuration)

    with respx.mock:
        respx.post(f"{client._base}{client._route}").mock(
            side_effect=httpx.ConnectError("connexion refusée")
        )
        with pytest.raises(RuntimeError) as exc:
            client.pose_question("Test ?")

    assert "Serveur MQC injoignable" in str(exc.value)


@pytest.mark.parametrize("valeur_donnee", ["foo", "bar", "fou42", "bar42"])
def test_methode_desinfecte_prefixe_retourne_a_l_identique_contenu_alphanumerique(
    valeur_donnee: str,
):
    valeur_desinfectee = EcrivainSortie._desinfecte_prefixe(valeur_donnee)
    assert valeur_desinfectee == valeur_donnee


@pytest.mark.parametrize(
    "valeur_infectee, valeur_desinfectee_attendue",
    [("foo/", "foo_"), ("bar*", "bar_"), ("bar.", "bar_"), ("bar./*", "bar___")],
)
def test_methode_desinfecte_prefixe_nettoie_le_contenu_non_alphanumerique(
    valeur_infectee, valeur_desinfectee_attendue
):
    valeur_desinfectee = EcrivainSortie._desinfecte_prefixe(valeur_infectee)
    assert valeur_desinfectee == valeur_desinfectee_attendue
