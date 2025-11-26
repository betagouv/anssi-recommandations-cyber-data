import logging
from argparse import ArgumentParser
from pathlib import Path

from adaptateurs.journal import (
    AdaptateurJournal,
    Donnees,
    TypeEvenement,
    fabrique_adaptateur_journal,
)
from journalisation.experience import EntrepotExperience, fabrique_entrepot_experience
from lecteur_csv import LecteurCSV


def consigne_evaluation(
    id_experience: int,
    entrepot_experience: EntrepotExperience,
    adaptateur_journal: AdaptateurJournal,
    fichier_questions_reponses: Path | None,
) -> None:
    resultat_evaluation = entrepot_experience.lit(id_experience)

    if resultat_evaluation is not None and fichier_questions_reponses is not None:
        lecteur_csv = LecteurCSV(fichier_questions_reponses)
        for evaluation in resultat_evaluation.metriques:
            informations_de_la_ligne = (
                lecteur_csv.recupere_les_informations_de_la_ligne(
                    evaluation["numero_ligne"]
                )
            )
            del evaluation["numero_ligne"]
            donnees_evaluation = Donnees.model_validate(
                {
                    "id_experimentation": resultat_evaluation.id_experimentation,
                    **informations_de_la_ligne,
                    **evaluation,
                }
            )
            adaptateur_journal.enregistre(
                TypeEvenement.EVALUATION_CALCULEE,
                donnees_evaluation,
            )
    adaptateur_journal.ferme_connexion()


def main() -> None:
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument(
        "--id-experience", required=True, type=str, help="Id de l’expérience en cours"
    )
    args = p.parse_args()
    id_experience = args.id_experience

    logging.info(f"Début de la consignation pour l'expérience {id_experience}")

    try:
        consigne_evaluation(
            id_experience=id_experience,
            entrepot_experience=fabrique_entrepot_experience(),
            adaptateur_journal=fabrique_adaptateur_journal(),
            fichier_questions_reponses=None,
        )
        logging.info(
            f"Consignation terminée avec succès pour l'expérience {id_experience}"
        )
    except Exception as e:
        logging.info(f"Erreur lors de la consignation: {e}")
        raise

    logging.info("Script terminé - arrêt normal")
    exit(0)


if __name__ == "__main__":
    main()
