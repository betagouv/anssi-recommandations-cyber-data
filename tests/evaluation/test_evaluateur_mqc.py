import glob
import uuid
from pathlib import Path

import httpx
import pytest
import respx

from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement
from configuration import Configuration
from evaluation.evaluateur_mqc import evaluateur_mqc
from evaluation.mqc.lanceur_deepeval import LanceurEvaluationDeepeval
from evaluation.mqc.remplisseur_reponses import (
    construit_base_url,
    formate_route_pose_question,
    ClientMQCHTTPAsync,
)
from infra.memoire.ecrivain import EcrivainSortieDeTest
from journalisation.evaluation import EntrepotEvaluationMemoire


@respx.mock
@pytest.mark.asyncio
async def test_execute_la_collecte_des_reponses_pour_creer_le_fichier_de_resultat_de_collecte(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    resultat_collecte_mqc,
    evaluateur_de_test_simple,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )
    entree = cree_fichier_csv_avec_du_contenu("Question type\nA?\n", tmp_path)
    ecrivain_sortie_de_test, sortie = resultat_collecte_mqc()
    entrepot_evaluation = EntrepotEvaluationMemoire()

    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_simple
    )
    await evaluateur_mqc(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        EntrepotEvaluationMemoire(),
        AdaptateurJournalMemoire(),
        lanceur_evaluation,
    )

    assert sortie.exists()
    collectes = glob.glob(str(sortie) + "/*")
    assert Path(collectes[0]).name.startswith("prefixe_") is True


@respx.mock
@pytest.mark.asyncio
async def test_lance_l_evaluation_avec_deepeval(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    evaluateur_de_test_simple,
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
    entrepot_evaluation = EntrepotEvaluationMemoire()
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_simple
    )

    id_evaluation_cree = await evaluateur_mqc(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        entrepot_evaluation,
        AdaptateurJournalMemoire(),
        lanceur_evaluation,
    )

    assert isinstance(id_evaluation_cree, str) is True
    assert est_uuid_valide(id_evaluation_cree) is True


def est_uuid_valide(uuid_a_tester):
    try:
        uuid.UUID(uuid_a_tester, version=4)
    except ValueError:
        return False
    return True


@respx.mock
@pytest.mark.asyncio
async def test_consigne_les_resultats_d_evaluation(
    tmp_path: Path,
    configuration: Configuration,
    cree_fichier_csv_avec_du_contenu,
    reponse_avec_paragraphes,
    resultat_collecte_mqc,
    evaluateur_de_test_simple,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )
    entree = cree_fichier_csv_avec_du_contenu("Question type\nA?\n", tmp_path)
    ecrivain_sortie_de_test, sortie = resultat_collecte_mqc()
    entrepot_evaluation = EntrepotEvaluationMemoire()

    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_simple
    )

    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()
    await evaluateur_mqc(
        entree,
        "prefixe",
        ecrivain_sortie_de_test,
        1,
        ClientMQCHTTPAsync(cfg=configuration.mqc),
        entrepot_evaluation,
        adaptateur_journal,
        lanceur_evaluation,
    )

    assert (
        adaptateur_journal.les_evenements()[0]["type"]
        == TypeEvenement.EVALUATION_CALCULEE
    )

    donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    assert donnees_recues["id_experimentation"] is not None
    assert donnees_recues["une_metrique"] == 1.0
