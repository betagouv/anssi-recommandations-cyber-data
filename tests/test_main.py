import glob
import uuid
from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest
import respx

from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement
from configuration import Configuration
from evaluation.lanceur_deepeval import LanceurExperienceDeepeval
from experience.experience import LanceurExperienceEvalap
from infra.memoire.ecrivain import EcrivainSortieDeTest
from infra.memoire.evalap import EvalapClientDeTest
from journalisation.experience import EntrepotExperienceMemoire
from main import main
from mqc.remplisseur_reponses import (
    ClientMQCHTTPAsync,
    construit_base_url,
    formate_route_pose_question,
)


@respx.mock
@pytest.mark.asyncio
async def test_execute_la_collecte_des_reponses_pour_creer_le_fichier_de_resultat_de_collecte(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    resultat_collecte_mqc,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )
    entree = cree_fichier_csv_avec_du_contenu("Question type\nA?\n", tmp_path)
    ecrivain_sortie_de_test, sortie = resultat_collecte_mqc()
    session = Mock()
    client = EvalapClientDeTest(configuration, session=session)

    lanceur_experience = LanceurExperienceEvalap(client, configuration)
    await main(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        EntrepotExperienceMemoire(),
        AdaptateurJournalMemoire(),
        lanceur_experience,
    )

    assert sortie.exists()
    collectes = glob.glob(str(sortie) + "/*")
    assert Path(collectes[0]).name.startswith("prefixe_") is True


@respx.mock
@pytest.mark.asyncio
async def test_lance_l_experience(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    une_experience_evalap,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )
    client = une_experience_evalap(configuration)
    entree = cree_fichier_csv_avec_du_contenu("Question type\nA?\n", tmp_path)
    contenu_fichier_csv_resultat_collecte = "REF Guide,REF Question,Que stion type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\nGAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]"
    ecrivain_sortie_de_test = EcrivainSortieDeTest(
        contenu_fichier_csv_resultat_collecte
    )
    lanceur_experience = LanceurExperienceEvalap(client, configuration)

    id_experience_cree = await main(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        EntrepotExperienceMemoire(),
        AdaptateurJournalMemoire(),
        lanceur_experience,
    )

    assert id_experience_cree == 1


@respx.mock
@pytest.mark.asyncio
async def test_lance_l_experience_avec_deepeval(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    une_experience_evalap,
    evaluateur_de_test,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )
    entree = cree_fichier_csv_avec_du_contenu("Question type\nA?\n", tmp_path)
    en_tete = "REF Guide,REF Question,Question type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\n"
    premiere_ligne = "GAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]"
    contenu_fichier_csv_resultat_collecte = en_tete + premiere_ligne
    ecrivain_sortie_de_test = EcrivainSortieDeTest(
        contenu_fichier_csv_resultat_collecte
    )
    entrepot_experience = EntrepotExperienceMemoire()
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_de_test
    )

    id_experience_cree = await main(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        entrepot_experience,
        AdaptateurJournalMemoire(),
        lanceur_experience,
    )

    assert isinstance(id_experience_cree, str) is True
    assert est_uuid_valide(id_experience_cree) is True


def est_uuid_valide(uuid_a_tester):
    try:
        uuid.UUID(uuid_a_tester, version=4)
    except ValueError:
        return False
    return True


@respx.mock
@pytest.mark.asyncio
async def test_consigne_les_resultats_d_experience(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    resultat_collecte_mqc,
    resultat_experience,
    une_experience_evalap,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )
    client = une_experience_evalap(configuration)
    entree = cree_fichier_csv_avec_du_contenu("Question type\nA?\n", tmp_path)
    ecrivain_sortie_de_test, sortie = resultat_collecte_mqc()
    lanceur_experience = LanceurExperienceEvalap(client, configuration)

    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()
    await main(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        resultat_experience,
        adaptateur_journal,
        lanceur_experience,
    )

    assert (
        adaptateur_journal.les_evenements()[0]["type"]
        == TypeEvenement.EVALUATION_CALCULEE
    )

    donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    assert donnees_recues["id_experimentation"] == 1
    assert donnees_recues["score_numero_page_en_contexte_4"] == 0.4
    assert donnees_recues["bon_nom_document_en_contexte_2"] == 0
