import pandas as pd

from adaptateurs.journal import AdaptateurJournal, Donnees, TypeEvenement


def consigne_evaluation(df: pd.DataFrame, adaptateur_journal: AdaptateurJournal):
    contenu_evaluation = df.to_dict("records")
    for evaluation in contenu_evaluation:
        donnees_evaluation = Donnees.model_validate(evaluation)
        adaptateur_journal.consigne_evenement(
            TypeEvenement.EVALUATION_CALCULEE,
            donnees_evaluation,
        )
