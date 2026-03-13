import argparse

import requests

from adaptateurs.client_albert_reformulation_reel import ClientAlbertReformulationReel
from adaptateurs.clients_albert import ClientAlbertReformulation
from configuration import recupere_configuration, Configuration
from evaluation.reformulation.evaluation import (
    EvaluateurReformulation,
    QuestionAEvaluer,
    ResultatEvaluation,
)


def lance_evaluation(
    client_albert: ClientAlbertReformulation,
    prompt: str,
    questions: list[QuestionAEvaluer],
) -> list[ResultatEvaluation]:
    return EvaluateurReformulation(client_albert, prompt).evalue(questions=questions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url-prompt", required=True, help="URL où se procurer le prompt (Github)"
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
    resultat = lance_evaluation(
        client_albert,
        prompt.text,
        [
            QuestionAEvaluer(
                "Qu’est-ce qu’une attaque DDOS ?", "Qu’est-ce qu’une attaque DDOS ?"
            )
        ],
    )
    print(f"RESULTAT : {resultat}")
