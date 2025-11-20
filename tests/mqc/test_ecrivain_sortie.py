from pathlib import Path

import httpx
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


def initialise(
    configuration_mqc: MQC,
    fichier: Path,
    reponse_attendue: httpx.Response,
    sous_dossier: Path,
    chemin_racine: Path,
) -> tuple[RemplisseurReponses, LecteurCSV, EcrivainSortie]:
    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)
    respx.post(f"{base}{chemin}").mock(return_value=reponse_attendue)
    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ecrivain = EcrivainSortie(
        racine=chemin_racine, sous_dossier=sous_dossier, horloge=(HorlogeSysteme())
    )
    return remplisseur, lecteur, ecrivain


@respx.mock
@pytest.mark.asyncio
async def test_ecriture_cree_fichier_dans_bon_dossier(
    tmp_path: Path,
    configuration_mqc: MQC,
    reponse_creation_experience,
    fichier_evaluation,
):
    sous_dossier = Path("donnees/sortie")
    fichier = fichier_evaluation("Question type\nA?\n", sous_dossier)
    reponse_attendue = reponse_creation_experience("OK", "A?")
    remplisseur, lecteur, ecrivain = initialise(
        configuration_mqc, fichier, reponse_attendue, sous_dossier, tmp_path
    )

    ligne_enrichie = (await remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(
        ligne_enrichie, prefixe="evaluation"
    )

    assert chemin_csv.parent == tmp_path / "donnees" / "sortie"


@respx.mock
@pytest.mark.asyncio
async def test_ecriture_nom_fichier_contient_date(
    tmp_path: Path,
    configuration_mqc: MQC,
    reponse_creation_experience,
    fichier_evaluation,
):
    sous_dossier = Path("donnees/sortie")
    fichier = fichier_evaluation("Question type\nA?\n", sous_dossier)
    reponse_attendue = reponse_creation_experience("OK", "A?")
    remplisseur, lecteur, ecrivain = initialise(
        configuration_mqc, fichier, reponse_attendue, sous_dossier, tmp_path
    )

    ligne_enrichie = (await remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(
        ligne_enrichie, prefixe="evaluation"
    )

    assert "evaluation_" in chemin_csv.name


@respx.mock
@pytest.mark.asyncio
async def test_ecriture_contenu_csv_complet(
    tmp_path: Path,
    configuration_mqc: MQC,
    reponse_creation_experience,
    fichier_evaluation,
):
    fichier = fichier_evaluation("Question type\nA?\nB?\n")
    reponse_attendue = reponse_creation_experience("OK", "A?")
    remplisseur, lecteur, ecrivain = initialise(
        configuration_mqc, fichier, reponse_attendue, Path("donnees/sortie"), tmp_path
    )

    ligne1_enrichie = (await remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    ligne2_enrichie = (await remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne1_enrichie, "evaluation")
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne2_enrichie, "evaluation")

    contenu = chemin_csv.read_text(encoding="utf-8").splitlines()
    assert len(contenu) == 3
    assert "Question type,Réponse Bot" in contenu[0]
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
