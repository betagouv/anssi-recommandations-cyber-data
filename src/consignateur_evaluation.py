import io
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

import pandas as pd

from adaptateurs.journal import (
    AdaptateurJournal,
    Donnees,
    TypeEvenement,
    fabrique_adaptateur_journal,
)


def consigne_evaluation(
    resultats_metriques: Union[pd.DataFrame, bytes],
    adaptateur_journal: AdaptateurJournal,
):
    match resultats_metriques:
        case pd.DataFrame():
            contenu_evaluation = resultats_metriques.to_dict("records")
        case bytes():
            contenu_evaluation = pd.read_pickle(
                io.BytesIO(resultats_metriques)
            ).to_dict("records")

    for evaluation in contenu_evaluation:
        donnees_evaluation = Donnees.model_validate(evaluation)
        adaptateur_journal.consigne_evenement(
            TypeEvenement.EVALUATION_CALCULEE,
            donnees_evaluation,
        )


def main() -> None:
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    args = p.parse_args()
    df_evaluation = pd.read_csv(args.csv)

    consigne_evaluation(
        resultats_metriques=df_evaluation,
        adaptateur_journal=fabrique_adaptateur_journal(),
    )


if __name__ == "__main__":
    main()
