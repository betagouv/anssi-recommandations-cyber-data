import numpy as np


def _metrique_bon_nom_document_en_contexte(
    nom_document_reponse_bot: str = "",
    nom_document_verite_terrain: str = "",
) -> tuple[float, str]:
    score = 1.0 if nom_document_reponse_bot == nom_document_verite_terrain else 0.0

    if nom_document_verite_terrain == "":
        score = 0.0
        observation = "Aucun nom fourni"
    elif score == 1.0:
        observation = "Nom de document correct"
    else:
        observation = f"Nom de document incorrect: attendu '{nom_document_verite_terrain}' mais obtenu '{nom_document_reponse_bot}'"

    return score, observation


def _metrique_bon_numero_page_en_contexte(
    numero_page_reponse_bot: int,
    numero_page_verite_terrain: int,
) -> tuple[float, str]:
    try:
        page_estimee = int(numero_page_reponse_bot)
        page_verite = int(numero_page_verite_terrain)
    except (ValueError, TypeError):
        return 0.0, "Numéro de page invalide"

    if page_estimee == page_verite:
        return 1.0, "Numéro de page correct"
    else:
        return 0.0, "Numéro de page incorrect"


def _metrique_score_numero_page_en_contexte(
    numero_page_reponse_bot=int,
    numero_page_verite_terrain=int,
) -> tuple[float, str]:
    if numero_page_reponse_bot is None or numero_page_verite_terrain is None:
        return 0.0, "Numéro de page manquant"

    try:
        page_estimee = int(numero_page_reponse_bot)
        page_verite = int(numero_page_verite_terrain)
    except (ValueError, TypeError):
        return 0.0, "Numéro de page invalide"

    if page_estimee == page_verite:
        return 1.0, "Numéro de page correct"

    distance = abs(page_estimee - page_verite)
    max_distance = 10
    distance_normalisee = min(distance / max_distance, 1.0)
    penalite = float(1 - np.exp(-1.5 * np.sqrt(distance_normalisee)))

    score = 1.0 - penalite
    score = round(score, 2)

    if score == 1.0:
        observation = "Numéro de page correct"
    elif score <= 0.25:
        observation = (
            f"Numéro de page erreur importante: {page_estimee} vs {page_verite}"
        )
    else:
        observation = f"Numéro de page proche: {page_estimee} vs {page_verite} (score: {score:.2f})"

    return score, observation
