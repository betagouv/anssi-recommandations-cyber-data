import asyncio
from pathlib import Path
import pytest
import respx
from configuration import MQC
from lecteur_csv import LecteurCSV
from mqc.ecrivain_sortie import HorlogeSysteme, EcrivainSortie
from mqc.remplisseur_reponses import (
    construit_base_url,
    formate_route_pose_question,
    ClientMQCHTTPAsync,
    RemplisseurReponses,
)
from tests.mqc.test_remplisseur_pose_question import cree_reponse_mock


@respx.mock
def test_ecriture_cree_fichier_dans_bon_dossier(tmp_path: Path, configuration_mqc: MQC):
    (tmp_path / "donnees" / "sortie").mkdir(parents=True, exist_ok=True)
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)
    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("OK", "A?"))

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(
        ligne_enrichie, prefixe="evaluation"
    )

    assert chemin_csv.parent == tmp_path / "donnees" / "sortie"


@respx.mock
def test_ecriture_nom_fichier_contient_date(tmp_path: Path, configuration_mqc: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)
    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("OK", "A?"))

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(
        ligne_enrichie, prefixe="evaluation"
    )

    assert "evaluation_" in chemin_csv.name


@respx.mock
def test_ecriture_contenu_csv_complet(tmp_path: Path, configuration_mqc: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\nB?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)
    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("OK", "A?"))

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )

    ligne1_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne1_enrichie, "evaluation")

    ligne2_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne2_enrichie, "evaluation")

    contenu = chemin_csv.read_text(encoding="utf-8").splitlines()
    assert contenu[0].startswith("Question type")
    assert "A?,OK" in contenu[1]
    assert "B?,OK" in contenu[2]


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


@respx.mock
def test_ecrit_ligne_depuis_lecteur_csv_ecrit_ligne_par_ligne(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("reponse_test", "Q1?")
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("sortie"), horloge=horloge
    )

    ligne1_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    chemin_sortie = ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne1_enrichie, "test")

    contenu = chemin_sortie.read_text(encoding="utf-8").strip().split("\n")
    assert len(contenu) == 2
    assert "Question type,Réponse Bot" in contenu[0]
    assert "Q1?,reponse_test" in contenu[1]

    ligne2_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne2_enrichie, "test")

    contenu = chemin_sortie.read_text(encoding="utf-8").strip().split("\n")
    assert len(contenu) == 3
    assert "Q2?,reponse_test" in contenu[2]
