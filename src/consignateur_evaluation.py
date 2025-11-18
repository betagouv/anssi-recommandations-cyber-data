from argparse import ArgumentParser

from adaptateurs.journal import (
    AdaptateurJournal,
    Donnees,
    TypeEvenement,
    fabrique_adaptateur_journal,
)
from journalisation.experience import EntrepotExperience


def consigne_evaluation(
    id_experience: int,
    entrepot_experience: EntrepotExperience,
    adaptateur_journal: AdaptateurJournal,
) -> None:
    resultat_evaluation = entrepot_experience.lit(id_experience)

    if resultat_evaluation is not None:
        for evaluation in resultat_evaluation.metriques:
            del evaluation["numero_ligne"]
            donnees_evaluation = Donnees.model_validate(
                {
                    "id_experimentation": resultat_evaluation.id_experimentation,
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

    consigne_evaluation(
        id_experience=id_experience,
        entrepot_experience=EntrepotExperience(),
        adaptateur_journal=fabrique_adaptateur_journal(),
    )


if __name__ == "__main__":
    main()
