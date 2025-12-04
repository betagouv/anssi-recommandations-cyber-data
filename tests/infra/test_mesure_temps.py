from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement
from infra.mesure_temps import mesurer_temps
from deepeval.test_case import LLMTestCase


def un_cas_de_test(nom: str) -> LLMTestCase:
    return LLMTestCase(name=nom, input="input")


def test_mesure_temps_consigne_dans_le_journal():
    adaptateur_journal_memoire = AdaptateurJournalMemoire()

    mesurer_temps(adaptateur_journal_memoire)(lambda: "Bonjour")()

    evenement_temps_execution = adaptateur_journal_memoire.les_evenements()[0]
    assert evenement_temps_execution["type"] == TypeEvenement.TEMPS_EVALUATION_MESURE
    assert evenement_temps_execution["donnees"]["nom_fonction"] == "<lambda>"
    assert evenement_temps_execution["donnees"]["duree"] > 0
    assert adaptateur_journal_memoire.ferme_connexion_a_ete_appelee == 1


def test_mesure_temps_consigne_dans_le_journal_avec_des_noms_de_cas_de_test():
    adaptateur_journal_memoire = AdaptateurJournalMemoire()

    mesurer_temps(adaptateur_journal_memoire)(lambda premier_argument, cas_de_test: "Bonjour")(
        "Le monde !",[un_cas_de_test("Test 1"), un_cas_de_test("Test 2")]
    )

    evenement_temps_execution = adaptateur_journal_memoire.les_evenements()[0]
    assert len(evenement_temps_execution["donnees"]["cas_de_test"]) == 14
    assert evenement_temps_execution["donnees"]["cas_de_test"] == "Test 1, Test 2"
