from pathlib import Path
from adaptateurs.journal import (
    AdaptateurJournal,
    Donnees,
    TypeEvenement,
)
from infra.lecteur_csv import LecteurCSV
from journalisation.experience import EntrepotExperience


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
