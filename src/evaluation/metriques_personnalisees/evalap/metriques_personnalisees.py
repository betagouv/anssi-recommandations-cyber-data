import numpy as np


def _metrique_bon_nom_document_en_contexte(
    nom_document_reponse_bot: str = "",
    nom_document_verite_terrain: str = "",
) -> float:
    if nom_document_verite_terrain == "":
        return 0.0

    return 1.0 if nom_document_reponse_bot == nom_document_verite_terrain else 0.0


def _metrique_bon_numero_page_en_contexte(
    numero_page_reponse_bot: int,
    numero_page_verite_terrain: int,
) -> float:
    try:
        page_estimee = int(numero_page_reponse_bot)
        page_verite = int(numero_page_verite_terrain)
    except (ValueError, TypeError):
        return 0.0

    return 1.0 if page_estimee == page_verite else 0.0


def _metrique_score_numero_page_en_contexte(
    numero_page_reponse_bot=int,
    numero_page_verite_terrain=int,
) -> float:
    if numero_page_reponse_bot is None or numero_page_verite_terrain is None:
        return 0.0

    try:
        page_estimee = int(numero_page_reponse_bot)
        page_verite = int(numero_page_verite_terrain)
    except (ValueError, TypeError):
        return 0.0

    if page_estimee == page_verite:
        return 1.0

    distance = abs(page_estimee - page_verite)
    max_distance = 10
    distance_normalisee = min(distance / max_distance, 1.0)
    penalite = float(1 - np.exp(-1.5 * np.sqrt(distance_normalisee)))

    score = 1.0 - penalite
    return round(score, 2)
