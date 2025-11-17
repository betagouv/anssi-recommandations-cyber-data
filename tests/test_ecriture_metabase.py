import pandas as pd
from adaptateurs.journal import TypeEvenement, AdaptateurJournalMemoire
from consignateur_evaluation import consigne_evaluation
import io


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


def test_consigne_evenement_suite_recuperation_fichier_sortie_evaluation_evalap_au_format_byte():
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
    tampon = io.BytesIO()
    df.to_pickle(tampon)
    donnees_byte = tampon.getvalue()

    consigne_evaluation(donnees_byte, adaptateur_journal)

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
