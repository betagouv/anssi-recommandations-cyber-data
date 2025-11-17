from adaptateurs.journal import TypeEvenement, AdaptateurJournalMemoire
from consignateur_evaluation import consigne_evaluation

from journalisation.experience import Experience, EntrepotExperienceMemoire


def test_consigne_evenement_suite_recuperation_fichier_sortie_evaluation_evalap():
    entrepot_experience = EntrepotExperienceMemoire()
    (
        entrepot_experience.persiste(
            Experience(
                id_experimentation=1,
                metriques=[
                    {
                        "numero_ligne": 1,
                        "score_numero_page_en_contexte_4": 0.4,
                        "bon_nom_document_en_contexte_2": 0,
                    }
                ],
            )
        ),
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(1, entrepot_experience, adaptateur_journal)

    assert (
        adaptateur_journal.les_evenements()[0]["type"]
        == TypeEvenement.EVALUATION_CALCULEE
    )
    assert adaptateur_journal.les_evenements()[0]["donnees"] == {
        "id_experimentation": 1,
        "score_numero_page_en_contexte_4": 0.4,
        "bon_nom_document_en_contexte_2": 0,
    }


def test_consigne_les_evenements_suite_recuperation_fichier_sortie_evaluation_evalap():
    entrepot_experience = EntrepotExperienceMemoire()
    (
        entrepot_experience.persiste(
            Experience(
                id_experimentation=2,
                metriques=[
                    {
                        "numero_ligne": 1,
                        "score_numero_page_en_contexte_4": 0.6,
                        "bon_nom_document_en_contexte_2": 1,
                    },
                    {
                        "numero_ligne": 2,
                        "score_numero_page_en_contexte_4": 0.7,
                        "bon_nom_document_en_contexte_2": 0,
                    },
                ],
            )
        ),
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(2, entrepot_experience, adaptateur_journal)

    les_evenements = adaptateur_journal.les_evenements()
    assert len(les_evenements) == 2
    assert les_evenements[0]["donnees"] == {
        "id_experimentation": 2,
        "score_numero_page_en_contexte_4": 0.6,
        "bon_nom_document_en_contexte_2": 1,
    }
    assert les_evenements[1]["donnees"] == {
        "id_experimentation": 2,
        "score_numero_page_en_contexte_4": 0.7,
        "bon_nom_document_en_contexte_2": 0,
    }


def test_consigne_les_evenements_extrait_dynamiquement_le_nom_des_colonnes():
    entrepot_experience = EntrepotExperienceMemoire()
    (
        entrepot_experience.persiste(
            Experience(
                id_experimentation=1,
                metriques=[
                    {
                        "numero_ligne": 1,
                        "score_numero_page_en_contexte_4": 0.7,
                        "nouvelle_metrique": 0,
                    }
                ],
            )
        ),
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(1, entrepot_experience, adaptateur_journal)

    les_evenements = adaptateur_journal.les_evenements()
    assert les_evenements[0]["donnees"] == {
        "id_experimentation": 1,
        "score_numero_page_en_contexte_4": 0.7,
        "nouvelle_metrique": 0,
    }


def test_ne_consigne_pas_si_pas_d_evaluation():
    entrepot_experience = EntrepotExperienceMemoire()
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(1, entrepot_experience, adaptateur_journal)

    les_evenements = adaptateur_journal.les_evenements()
    assert len(les_evenements) == 0


def test_ferme_la_connexion_apres_un_enregistrement() -> None:
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=2,
            metriques=[
                {
                    "numero_ligne": 1,
                    "score_numero_page_en_contexte_4": 0.6,
                    "bon_nom_document_en_contexte_2": 1,
                },
                {
                    "numero_ligne": 2,
                    "score_numero_page_en_contexte_4": 0.7,
                    "bon_nom_document_en_contexte_2": 0,
                },
            ],
        )
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(2, entrepot_experience, adaptateur_journal)

    assert adaptateur_journal.ferme_connexion_a_ete_appelee == 1
