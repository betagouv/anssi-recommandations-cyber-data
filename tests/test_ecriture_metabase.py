import pandas as pd
from adaptateurs.journal import AdaptateurJournal, TypeEvenement, Donnees


class AdaptateurJournalMemoire(AdaptateurJournal):
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        self._evenements.append({"type": type, "donnees": donnees.model_dump()})

    def __init__(self):
        self._evenements = []

    def enregistrer(self, evenement):
        self._evenements.append(evenement)

    def les_evenements(self):
        return self._evenements


def consigne_evaluation(df: pd.DataFrame, adaptateur_journal: AdaptateurJournal):
    contenu_evaluation = df.to_dict("records")
    for evaluation in contenu_evaluation:
        donnees_evaluation = Donnees.model_validate(evaluation)
        adaptateur_journal.consigne_evenement(
            TypeEvenement.EVALUATION_CALCULEE,
            donnees_evaluation,
        )


def test_consigne_evenement_suite_recuperation_fichier_sortie_evaluation_evalap():
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()
    df = pd.DataFrame(
        [
            {
                "id_experimentation": 1,
                "score_numero_page_en_contexte_4": 0.4,
                "bon_nom_document_en_contexte_2": 0,
            }
        ]
    )

    consigne_evaluation(df, adaptateur_journal)

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
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()
    df = pd.DataFrame(
        [
            {
                "id_experimentation": 1,
                "score_numero_page_en_contexte_4": 0.6,
                "bon_nom_document_en_contexte_2": 1,
            },
            {
                "id_experimentation": 1,
                "score_numero_page_en_contexte_4": 0.7,
                "bon_nom_document_en_contexte_2": 0,
            },
        ]
    )

    consigne_evaluation(df, adaptateur_journal)

    les_evenements = adaptateur_journal.les_evenements()
    assert len(les_evenements) == 2
    assert les_evenements[0]["donnees"] == {
        "id_experimentation": 1,
        "score_numero_page_en_contexte_4": 0.6,
        "bon_nom_document_en_contexte_2": 1,
    }
    assert les_evenements[1]["donnees"] == {
        "id_experimentation": 1,
        "score_numero_page_en_contexte_4": 0.7,
        "bon_nom_document_en_contexte_2": 0,
    }


def test_consigne_les_evenements_extrait_dynamiquement_le_nom_des_colonnes():
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()
    df_different = pd.DataFrame(
        [
            {
                "id_experimentation": 1,
                "score_numero_page_en_contexte_4": 0.7,
                "nouvelle_metrique": 0,
            }
        ]
    )

    consigne_evaluation(df_different, adaptateur_journal)

    les_evenements = adaptateur_journal.les_evenements()
    assert les_evenements[0]["donnees"] == {
        "id_experimentation": 1,
        "score_numero_page_en_contexte_4": 0.7,
        "nouvelle_metrique": 0,
    }
