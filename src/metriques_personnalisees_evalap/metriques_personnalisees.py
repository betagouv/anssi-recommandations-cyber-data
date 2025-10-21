def _metrique_bon_nom_document_en_contexte(
    nom_document_reponse_bot: str = "",
    nom_document_verite_terrain: str = "",
):
    score = 1.0 if nom_document_reponse_bot == nom_document_verite_terrain else 0.0

    if nom_document_verite_terrain == "":
        score = 0.0
        observation = "Aucun nom fourni"
    elif score == 1.0:
        observation = "Nom de document correct"
    else:
        observation = f"Nom de document incorrect: attendu '{nom_document_verite_terrain}' mais obtenu '{nom_document_reponse_bot}'"

    return score, observation, {}
