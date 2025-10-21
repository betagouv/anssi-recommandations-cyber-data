from . import metric_registry  # type: ignore[attr-defined]
import math


@metric_registry.register(
    name="bon_numero_page_en_contexte",
    description="Vérifie la proximité des numéros de page entre contexte et vérité terrain",
    metric_type="llm",
    require=["numero_page_reponse_bot", "numero_page_verite_terrain"],
)
def metrique_bon_numero_page_en_contexte(output, output_true, **kwargs):
    numero_page_reponse_bot = kwargs.get("numero_page_reponse_bot")
    numero_page_verite_terrain = kwargs.get("numero_page_verite_terrain")

    if numero_page_reponse_bot is None or numero_page_verite_terrain is None:
        return 0.0, "Numéro de page manquant", {}

    try:
        page_bot = int(numero_page_reponse_bot)
        page_verite = int(numero_page_verite_terrain)
    except (ValueError, TypeError):
        return 0.0, "Numéro de page invalide", {}

    if page_bot == page_verite:
        return 1.0, "Numéro de page correct", {}

    distance = abs(page_bot - page_verite)

    score = math.exp(-distance / 3.0)
    score = round(score, 2)

    if distance == 1:
        observation = (
            f"Numéro de page proche: {page_bot} vs {page_verite} (distance: {distance})"
        )
    elif distance <= 3:
        observation = f"Numéro de page moyennement éloigné: {page_bot} vs {page_verite} (distance: {distance})"
    else:
        observation = f"Numéro de page très éloigné: {page_bot} vs {page_verite} (distance: {distance})"

    return score, observation, {}
