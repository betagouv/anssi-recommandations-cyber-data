from . import metric_registry  # type: ignore[attr-defined]


@metric_registry.register(
    name="bon_nom_document_en_contexte",
    description="Vérifie si le nom du document en contexte correspond à celui attendu",
    metric_type="llm",  # paramètre trompeur mais c'est bien le type pour une métrique personnalisée non llm ...
    require=["nom_document_reponse_bot", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte(output, output_true, **kwargs):
    nom_document_reponse_bot = kwargs.get("nom_document_reponse_bot", "")
    nom_document_verite_terrain = kwargs.get("nom_document_verite_terrain", "")

    score = 1.0 if nom_document_reponse_bot == nom_document_verite_terrain else 0.0

    if score == 1.0:
        observation = "Nom de document correct"
    else:
        observation = f"Nom de document incorrect: attendu '{nom_document_verite_terrain}' mais obtenu '{nom_document_reponse_bot}'"

    return score, observation, {}
