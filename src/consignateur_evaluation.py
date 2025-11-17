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
    groupe = p.add_mutually_exclusive_group(required=True)
    groupe.add_argument("--csv", type=Path, help="Chemin du fichier CSV d'entrée")
    groupe.add_argument(
        "--bytes", type=Path, help="Contenu du fichier binaire d'entrée"
    )

    args = p.parse_args()
    if args.csv:
        contenu = pd.read_csv(args.csv)
    else:
        contenu = args.bytes.read_bytes()

    consigne_evaluation(
        resultats_metriques=contenu,
        adaptateur_journal=fabrique_adaptateur_journal(),
    )


if __name__ == "__main__":
    main()
