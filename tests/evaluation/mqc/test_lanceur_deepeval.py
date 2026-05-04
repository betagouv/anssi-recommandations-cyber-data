from pathlib import Path

from deepeval.metrics import (
    BaseMetric,
)

from evaluation.mqc.lanceur_deepeval import LanceurEvaluationDeepeval
from journalisation.evaluation import EntrepotEvaluationMemoire


def test_fabrique_lanceur_evaluation_transmet_chemin_mapping(
    tmp_path: Path, configuration, evaluateur_de_test_avec_metriques
):
    mapping_csv = tmp_path / "mapping.csv"
    mapping_csv.write_text(
        "REF,Nom,URL\nGAUT,Guide Auth,https://example.com/guide-fabrique.pdf\n",
        encoding="utf-8",
    )
    contenu_csv = (
        "REF Guide,REF Question,Question type,Tags,REF Réponse,Réponse envisagée,"
        "Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),"
        "Commentaire Note,Contexte,Noms Documents,Numéros Page\n"
        "GAUT,GAUT.Q.1,Question?,Usuelle,GAUT.R.1,réponse,10,en bas,réponse mqc,nan,OK,test,[],[]\n"
    )
    fichier_csv = tmp_path / "resultats.csv"
    fichier_csv.write_text(contenu_csv, encoding="utf-8")
    entrepot_evaluation = EntrepotEvaluationMemoire()

    lanceur = LanceurEvaluationDeepeval(
        entrepot_evaluation,
        evaluateur_de_test_avec_metriques,
    )
    lanceur.lance_l_evaluation(fichier_csv, mapping_csv)

    cas = evaluateur_de_test_avec_metriques.cas_de_test_executes[0]
    assert (
        cas.additional_metadata["nom_document_verite_terrain"] == "guide-fabrique.pdf"
    )


def test_evalue_un_jeu_de_donnees(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test_avec_metriques
):
    entrepot_evaluation = EntrepotEvaluationMemoire()
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_avec_metriques
    )

    id_evaluation = lanceur_evaluation.lance_l_evaluation(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
        Path("donnees/jointure-nom-guide.csv"),
    )

    evaluation_creee = entrepot_evaluation.lit(id_evaluation)
    assert evaluation_creee.metriques[0]["bon_nom_document_en_contexte_2"] == 1
    assert evaluation_creee.metriques[0]["bon_numero_page_en_contexte_2"] == 0
    assert evaluation_creee.metriques[0]["score_numero_page_en_contexte_2"] == 0.7
    assert evaluation_creee.metriques[0]["hallucination"] == 0.6


def test_evalue_un_jeu_de_donnees_avec_des_cas_de_test(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test_avec_metriques
):
    entrepot_evaluation = EntrepotEvaluationMemoire()

    evaluateur_deepeval = evaluateur_de_test_avec_metriques
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_deepeval
    )
    lanceur_evaluation.lance_l_evaluation(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
        Path("donnees/jointure-nom-guide.csv"),
    )

    assert len(evaluateur_deepeval.cas_de_test_executes) == 2
    # Vérifier les champs principaux du premier cas de test
    premier_cas = evaluateur_deepeval.cas_de_test_executes[0]
    assert premier_cas.input == "Qu'est-ce que l'authentification ?"
    assert premier_cas.actual_output == "réponse mqc"
    assert premier_cas.expected_output == "réponse envisagée"
    assert premier_cas.additional_metadata["numero_ligne"] == 0

    # Vérifier les champs principaux du deuxième cas de test
    deuxieme_cas = evaluateur_deepeval.cas_de_test_executes[1]
    assert deuxieme_cas.input == "Qu'elle est la bonne longueur d'un mot de passe?"
    assert deuxieme_cas.actual_output == "réponse mqc"
    assert deuxieme_cas.expected_output == "réponse envisagée"
    assert deuxieme_cas.additional_metadata["numero_ligne"] == 1


def test_evalue_un_jeu_de_donnees_avec_les_metriques_deepeval(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test_avec_metriques
):
    entrepot_evaluation = EntrepotEvaluationMemoire()

    evaluateur_deepeval = evaluateur_de_test_avec_metriques
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_deepeval
    )
    lanceur_evaluation.lance_l_evaluation(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
        Path("donnees/jointure-nom-guide.csv"),
    )

    assert evaluateur_deepeval.nombre_metriques_soumise == 19
    assert len(evaluateur_deepeval.metriques_deepeval_soumises) == 3
    assert (
        evaluateur_deepeval.metriques_deepeval_soumises[0].__name__ == "Hallucination"
    )
    assert (
        evaluateur_deepeval.metriques_deepeval_soumises[1].__name__
        == "Answer Relevancy"
    )
    assert evaluateur_deepeval.metriques_deepeval_soumises[2].__name__ == "Toxicity"


def test_evalue_un_jeu_de_donnees_avec_les_metriques_personnalisees(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test_avec_metriques
):
    entrepot_evaluation = EntrepotEvaluationMemoire()

    evaluateur_deepeval = evaluateur_de_test_avec_metriques
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_deepeval
    )
    lanceur_evaluation.lance_l_evaluation(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
        Path("donnees/jointure-nom-guide.csv"),
    )

    assert evaluateur_deepeval.nombre_metriques_soumise == 19
    assert len(evaluateur_deepeval.metriques_personnalisees_soumises) == 16
    assert (
        evaluateur_deepeval.metriques_personnalisees_soumises[0].__name__
        == "Longueur Réponse"
    )
    assert (
        les_metriques_portent_le_nom_aux_indices(
            evaluateur_deepeval.metriques_personnalisees_soumises,
            "Bon nom document en contexte",
            (1, 6),
        )
        is True
    )
    assert (
        les_metriques_portent_le_nom_aux_indices(
            evaluateur_deepeval.metriques_personnalisees_soumises,
            "Bon numéro page en contexte",
            (6, 11),
        )
        is True
    )
    assert (
        les_metriques_portent_le_nom_aux_indices(
            evaluateur_deepeval.metriques_personnalisees_soumises,
            "Score numéro page en contexte",
            (11, 16),
        )
        is True
    )


def test_evalue_un_jeu_de_donnees_et_retourne_le_numero_de_ligne(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test_avec_metriques
):
    entrepot_evaluation = EntrepotEvaluationMemoire()
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_avec_metriques
    )

    id_evaluation = lanceur_evaluation.lance_l_evaluation(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
        Path("donnees/jointure-nom-guide.csv"),
    )

    evaluation_creee = entrepot_evaluation.lit(id_evaluation)
    assert evaluation_creee.metriques[0]["numero_ligne"] == 0
    assert evaluation_creee.metriques[1]["numero_ligne"] == 1


def les_metriques_portent_le_nom_aux_indices(
    evaluateur_deepeval: list[BaseMetric], nom_attendu: str, indices: tuple
) -> bool:
    noms_attendus = []
    for i in range(0, indices[1] - indices[0]):
        noms_attendus.append(f"{nom_attendu} {i}")
    return noms_attendus == list(
        map(lambda m: m.__name__, evaluateur_deepeval[indices[0] : indices[1]])
    )
