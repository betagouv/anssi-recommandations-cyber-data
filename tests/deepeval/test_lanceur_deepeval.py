from evaluation.lanceur_deepeval import LanceurExperienceDeepeval
from journalisation.experience import (
    EntrepotExperienceMemoire,
)
from deepeval.metrics import (
    BaseMetric,
)


def test_evalue_un_jeu_de_donnees(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_de_test
    )

    id_experience = lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
    )

    experience_creee = entrepot_experience.lit(id_experience)
    assert experience_creee.metriques[0]["bon_nom_document_en_contexte_2"] == 1
    assert experience_creee.metriques[0]["bon_numero_page_en_contexte_2"] == 0
    assert experience_creee.metriques[0]["score_numero_page_en_contexte_2"] == 0.7
    assert experience_creee.metriques[0]["hallucination"] == 0.6


def test_evalue_un_jeu_de_donnees_avec_des_cas_de_test(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()

    evaluateur_deepeval = evaluateur_de_test
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_deepeval
    )
    lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
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
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()

    evaluateur_deepeval = evaluateur_de_test
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_deepeval
    )
    lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
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
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()

    evaluateur_deepeval = evaluateur_de_test
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_deepeval
    )
    lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
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
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_de_test
    )

    id_experience = lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
    )

    experience_creee = entrepot_experience.lit(id_experience)
    assert experience_creee.metriques[0]["numero_ligne"] == 0
    assert experience_creee.metriques[1]["numero_ligne"] == 1


def les_metriques_portent_le_nom_aux_indices(
    evaluateur_deepeval: list[BaseMetric], nom_attendu: str, indices: tuple
) -> bool:
    noms_attendus = []
    for i in range(0, indices[1] - indices[0]):
        noms_attendus.append(f"{nom_attendu} {i}")
    return noms_attendus == list(
        map(lambda m: m.__name__, evaluateur_deepeval[indices[0] : indices[1]])
    )
