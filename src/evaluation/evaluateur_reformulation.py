import argparse
from pathlib import Path

import requests

from adaptateurs.client_albert_reformulation_reel import ClientAlbertReformulationReel
from adaptateurs.clients_albert import ClientAlbertReformulation
from configuration import recupere_configuration, Configuration
from evaluation.reformulation.evaluation import (
    EvaluateurReformulation,
    QuestionAEvaluer,
    ResultatEvaluation,
)
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.evaluation.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)
from infra.lecteur_dataset_reformulation import LecteurDatasetReformulation


def lance_evaluation(
    client_albert: ClientAlbertReformulation,
    prompt: str,
    questions: list[QuestionAEvaluer],
) -> list[ResultatEvaluation]:
    return EvaluateurReformulation(
        client_albert,
        prompt,
        EvaluateurDeepevalMultiProcessus(),
        fabrique_bus_evenements(),
    ).evalue(questions=questions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url-prompt", required=True, help="URL où se procurer le prompt (Github)"
    )
    parser.add_argument(
        "--chemin-dataset",
        type=Path,
        default=Path(__file__).parent.parent / "donnees" / "dataset_reformulation.csv",
        help="Chemin vers le fichier CSV contenant les questions d'évaluation",
    )

    args = parser.parse_args()

    la_configuration: Configuration = recupere_configuration()
    client_albert = ClientAlbertReformulationReel(
        la_configuration.albert.url,
        la_configuration.albert.cle_api,
        la_configuration.albert.modele,
    )
    session = requests.Session()
    prompt = session.get(args.url_prompt)

    lecteur = LecteurDatasetReformulation(args.chemin_dataset)
    questions = lecteur.charge_questions()

    resultats = lance_evaluation(client_albert, prompt.text, questions)
    for resultat in resultats:
        print("=" * 80)
        print(f"Question originale    : {resultat.question}")
        print(f"Question reformulée   : {resultat.question_reformulee}")
        print(f"Reformulation idéale  : {resultat.reformulation_ideale}")
        print()
        if resultat.resultats[0].metrics_data:
            for metric_data in resultat.resultats[0].metrics_data:
                score_normalise = metric_data.score
                score_sur_dix = (
                    round(float(score_normalise) * 10, 1)
                    if score_normalise is not None
                    else None
                )
                print(f"  Métrique: {metric_data.name}")
                print(f"  Score (0-1): {score_normalise}")
                print(f"  Score (/10): {score_sur_dix}")
                print()
        print()
