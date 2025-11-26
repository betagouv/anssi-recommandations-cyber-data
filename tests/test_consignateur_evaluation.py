from adaptateurs.journal import TypeEvenement, AdaptateurJournalMemoire
from consignateur_evaluation import consigne_evaluation
from infra.memoire.ecrivain import EcrivainSortieDeTest

from journalisation.experience import Experience, EntrepotExperienceMemoire


def test_consigne_evenement_suite_recuperation_fichier_sortie_evaluation_evalap(
    resultat_collecte_mqc_avec_deux_resultats,
) -> None:
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=1,
            metriques=[
                {
                    "numero_ligne": 0,
                    "score_numero_page_en_contexte_4": 0.4,
                    "bon_nom_document_en_contexte_2": 0,
                }
            ],
        )
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(
        1,
        entrepot_experience,
        adaptateur_journal,
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
    )

    assert (
        adaptateur_journal.les_evenements()[0]["type"]
        == TypeEvenement.EVALUATION_CALCULEE
    )
    donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    assert donnees_recues["id_experimentation"] == 1
    assert donnees_recues["score_numero_page_en_contexte_4"] == 0.4
    assert donnees_recues["bon_nom_document_en_contexte_2"] == 0


def test_consigne_les_evenements_suite_recuperation_fichier_sortie_evaluation_evalap(
    resultat_collecte_mqc_avec_deux_resultats,
) -> None:
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=2,
            metriques=[
                {
                    "numero_ligne": 0,
                    "score_numero_page_en_contexte_4": 0.6,
                    "bon_nom_document_en_contexte_2": 1,
                },
                {
                    "numero_ligne": 1,
                    "score_numero_page_en_contexte_4": 0.7,
                    "bon_nom_document_en_contexte_2": 0,
                },
            ],
        )
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(
        2,
        entrepot_experience,
        adaptateur_journal,
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
    )

    les_evenements = adaptateur_journal.les_evenements()
    assert len(les_evenements) == 2

    premieres_donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    assert premieres_donnees_recues["id_experimentation"] == 2
    assert premieres_donnees_recues["score_numero_page_en_contexte_4"] == 0.6
    assert premieres_donnees_recues["bon_nom_document_en_contexte_2"] == 1

    secondes_donnees_recues = adaptateur_journal.les_evenements()[1]["donnees"]
    assert secondes_donnees_recues["id_experimentation"] == 2
    assert secondes_donnees_recues["score_numero_page_en_contexte_4"] == 0.7
    assert secondes_donnees_recues["bon_nom_document_en_contexte_2"] == 0


def test_consigne_les_evenements_extrait_dynamiquement_le_nom_des_colonnes(
    resultat_collecte_mqc_avec_deux_resultats,
) -> None:
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=1,
            metriques=[
                {
                    "numero_ligne": 0,
                    "score_numero_page_en_contexte_4": 0.7,
                    "nouvelle_metrique": 0,
                }
            ],
        )
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(
        1,
        entrepot_experience,
        adaptateur_journal,
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
    )

    donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    assert donnees_recues["id_experimentation"] == 1
    assert donnees_recues["score_numero_page_en_contexte_4"] == 0.7
    assert donnees_recues["nouvelle_metrique"] == 0


def test_ne_consigne_pas_si_pas_d_evaluation() -> None:
    entrepot_experience = EntrepotExperienceMemoire()
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(1, entrepot_experience, adaptateur_journal, None)

    les_evenements = adaptateur_journal.les_evenements()
    assert len(les_evenements) == 0


def test_ferme_la_connexion_apres_un_enregistrement(
    resultat_collecte_mqc_avec_deux_resultats,
) -> None:
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=2,
            metriques=[
                {
                    "numero_ligne": 0,
                    "score_numero_page_en_contexte_4": 0.6,
                    "bon_nom_document_en_contexte_2": 1,
                },
                {
                    "numero_ligne": 1,
                    "score_numero_page_en_contexte_4": 0.7,
                    "bon_nom_document_en_contexte_2": 0,
                },
            ],
        )
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(
        2,
        entrepot_experience,
        adaptateur_journal,
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant,
    )

    assert adaptateur_journal.ferme_connexion_a_ete_appelee == 1


def test_consigne_les_questions_reponses(
    cree_fichier_csv_avec_du_contenu,
) -> None:
    en_tete = "REF Guide,REF Question,Question type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\n"
    premiere_ligne = "GAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]\n"
    seconde_ligne = "GAUT,GAUT.Q.1,Qu'elle est la bonne longueur d'un mot de passe?,Usuelle,GAUT.R.1,réponse envisagée 2,10,en bas,réponse mqc 2,nan,Excellente réponse,test 2,[\"document_mot_de_passe\"],[42]\n"
    contenu_complet = en_tete + premiere_ligne + seconde_ligne
    ecrivain_sortie_de_test = EcrivainSortieDeTest(contenu_complet)
    ecrivain_sortie_de_test.ecris_contenu()
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=1,
            metriques=[
                {
                    "numero_ligne": 0,
                    "score_numero_page_en_contexte_4": 0.4,
                    "bon_nom_document_en_contexte_2": 0,
                },
                {
                    "numero_ligne": 1,
                    "score_numero_page_en_contexte_4": 0.5,
                    "bon_nom_document_en_contexte_2": 1,
                },
            ],
        )
    )
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()

    consigne_evaluation(
        1,
        entrepot_experience,
        adaptateur_journal,
        ecrivain_sortie_de_test._chemin_courant,
    )

    assert (
        adaptateur_journal.les_evenements()[0]["type"]
        == TypeEvenement.EVALUATION_CALCULEE
    )
    premieres_donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    secondes_donnees_recues = adaptateur_journal.les_evenements()[1]["donnees"]
    assert (
        premieres_donnees_recues["question_type"]
        == "Qu'est-ce que l'authentification ?"
    )
    assert premieres_donnees_recues["reponse_envisagee"] == "réponse envisagée"
    assert premieres_donnees_recues["reponse_bot"] == "réponse mqc"
    assert premieres_donnees_recues["noms_documents"] == []
    assert premieres_donnees_recues["numeros_page"] == []
    assert (
        secondes_donnees_recues["question_type"]
        == "Qu'elle est la bonne longueur d'un mot de passe?"
    )
    assert secondes_donnees_recues["reponse_envisagee"] == "réponse envisagée 2"
    assert secondes_donnees_recues["reponse_bot"] == "réponse mqc 2"
    assert secondes_donnees_recues["noms_documents"] == ["document_mot_de_passe"]
    assert secondes_donnees_recues["numeros_page"] == [42]
