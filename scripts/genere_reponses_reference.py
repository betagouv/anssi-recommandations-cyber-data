"""Génère les réponses de référence RAG pour le dataset d'évaluation ANSSI."""
from __future__ import annotations

import asyncio
import concurrent.futures
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ALBERT_URL: str = os.environ["ALBERT_URL"]
ALBERT_CLE_API: str = os.environ["ALBERT_CLE_API"]
ALBERT_MODELE: str = os.environ["ALBERT_MODELE"]
NB_WORKERS: int = int(os.getenv("NB_PROCESSUS_EN_PARALLELE_POUR_DEEPEVAL", "5"))

CSV_ENTREE = Path(__file__).parent.parent / "donnees/base_anssi_albert/questions_avec_verite_terrain_final.csv"
CSV_SORTIE = Path(__file__).parent.parent / "donnees/base_anssi_albert/questions_avec_verite_terrain_final_reponses.csv"

PROMPT_SYSTEME = """Tu es un expert en cybersécurité chargé de produire des réponses de référence pour un dataset RAG d'évaluation sur des documents ANSSI.

RÈGLES ABSOLUES — aucune exception :

1. SOURCES : Tu te bases UNIQUEMENT sur le CONTEXTE fourni. Chaque affirmation doit être vérifiable dans ce contexte. N'utilise jamais tes connaissances générales.

2. ARTEFACTS PDF DEUX COLONNES : Le contexte est extrait de PDFs en deux colonnes. L'extraction mélange parfois les colonnes ligne par ligne, ce qui produit des phrases incohérentes, des mots collés (ex. "Storeserviceandapplication", "Implementcertificate-based"), ou des thèmes qui alternent sans logique. Face à ces artefacts :
   - Lis le contexte en cherchant les fragments qui forment des phrases françaises ou anglaises cohérentes.
   - Ignore les fragments syntaxiquement incohérents ou qui semblent appartenir à une autre section du document.
   - Ne jamais inclure dans la réponse un élément dont tu n'es pas sûr qu'il répond bien à la question posée.

3. EXHAUSTIVITÉ : Couvre tous les points significatifs du contexte qui répondent directement à la question : listes (→, •, numérotées), définitions, conditions, exceptions, valeurs chiffrées. Ne saute aucun point pertinent.

4. PROPORTIONNALITÉ : La longueur de la réponse est strictement proportionnelle à la richesse du contexte. Un contexte court donne une réponse courte. N'étire pas la réponse au-delà de ce que le contexte contient.

5. CITATIONS DE SOURCES : Ne mentionne aucun nom de guide, document ou publication sauf s'il apparaît textuellement dans le contexte fourni.

6. FORMAT (impératif) :
   - Texte brut uniquement : pas de markdown, pas de gras (**), pas de titres (##), pas de code.
   - Paragraphes séparés par une ligne vide pour les réponses conceptuelles longues.
   - Listes avec tiret (-) uniquement si le contenu est une énumération naturelle ; chaque item se termine par ; sauf le dernier qui se termine par .
   - La réponse commence directement par le contenu, sans introduction généraliste.
   - La réponse se termine par un point.

ANTI-PATTERNS INTERDITS :
- Ajouter une information absente du contexte, même exacte
- Inclure un élément dont l'appartenance à la section est incertaine à cause des artefacts PDF
- Utiliser ** ou ## ou tout autre marqueur markdown
- Rédiger une phrase d'introduction ("Dans ce contexte...", "L'ANSSI recommande de...")
- Conclure avec une phrase de remplissage
- Citer une source non présente dans le contexte"""

PROMPT_UTILISATEUR = """QUESTION : {question}
TYPE : {question_type}

CONTEXTE COMPLET :
{contexte}

Génère la réponse RAG de référence en respectant strictement les règles du système."""


def genere_reponse(client: OpenAI, question: str, question_type: str, contexte: str) -> str:
    completion = client.chat.completions.create(
        model=ALBERT_MODELE,
        messages=[
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": PROMPT_UTILISATEUR.format(
                question=question, question_type=question_type, contexte=contexte
            )},
        ],
        stream=False,
        n=1,
    )
    return completion.choices[0].message.content or ""


async def genere_toutes_reponses(df: pd.DataFrame) -> list[str]:
    client = OpenAI(base_url=ALBERT_URL, api_key=ALBERT_CLE_API)

    def tache(row: pd.Series) -> str:
        return genere_reponse(client, row["Question"], row["Question type"], row["Contexte"])

    with concurrent.futures.ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
        loop = asyncio.get_running_loop()
        futures = [
            loop.run_in_executor(executor, tache, row)
            for _, row in df.iterrows()
        ]
        return list(await asyncio.gather(*futures))


def main() -> None:
    df = pd.read_csv(CSV_ENTREE).head(10)
    reponses = asyncio.run(genere_toutes_reponses(df))
    df["Réponse envisagée"] = reponses
    df.to_csv(CSV_SORTIE, index=False)
    print(f"Résultat écrit dans {CSV_SORTIE} ({len(df)} lignes)")


if __name__ == "__main__":
    main()
