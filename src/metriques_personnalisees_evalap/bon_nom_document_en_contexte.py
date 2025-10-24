from . import metric_registry  # type: ignore[attr-defined]


def _compare_documents(nom_document_reponse_bot: str, nom_document_verite_terrain: str):
    score = 1.0 if nom_document_reponse_bot == nom_document_verite_terrain else 0.0

    if score == 1.0:
        observation = "Nom de document correct"
    else:
        observation = f"Nom de document incorrect: attendu '{nom_document_verite_terrain}' mais obtenu '{nom_document_reponse_bot}'"

    return score, observation, {}


@metric_registry.register(
    name="bon_nom_document_en_contexte_0",
    description="Vérifie si le nom du document en contexte (position 0) correspond à celui attendu",
    metric_type="llm",
    require=["nom_document_reponse_bot_0", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte_0(output, output_true, **kwargs):
    nom_document_reponse_bot = kwargs.get("nom_document_reponse_bot_0", "")
    nom_document_verite_terrain = kwargs.get("nom_document_verite_terrain", "")
    return _compare_documents(nom_document_reponse_bot, nom_document_verite_terrain)


@metric_registry.register(
    name="bon_nom_document_en_contexte_1",
    description="Vérifie si le nom du document en contexte (position 1) correspond à celui attendu",
    metric_type="llm",
    require=["nom_document_reponse_bot_1", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte_1(output, output_true, **kwargs):
    nom_document_reponse_bot = kwargs.get("nom_document_reponse_bot_1", "")
    nom_document_verite_terrain = kwargs.get("nom_document_verite_terrain", "")
    return _compare_documents(nom_document_reponse_bot, nom_document_verite_terrain)


@metric_registry.register(
    name="bon_nom_document_en_contexte_2",
    description="Vérifie si le nom du document en contexte (position 2) correspond à celui attendu",
    metric_type="llm",
    require=["nom_document_reponse_bot_2", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte_2(output, output_true, **kwargs):
    nom_document_reponse_bot = kwargs.get("nom_document_reponse_bot_2", "")
    nom_document_verite_terrain = kwargs.get("nom_document_verite_terrain", "")
    return _compare_documents(nom_document_reponse_bot, nom_document_verite_terrain)


@metric_registry.register(
    name="bon_nom_document_en_contexte_3",
    description="Vérifie si le nom du document en contexte (position 3) correspond à celui attendu",
    metric_type="llm",
    require=["nom_document_reponse_bot_3", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte_3(output, output_true, **kwargs):
    nom_document_reponse_bot = kwargs.get("nom_document_reponse_bot_3", "")
    nom_document_verite_terrain = kwargs.get("nom_document_verite_terrain", "")
    return _compare_documents(nom_document_reponse_bot, nom_document_verite_terrain)


@metric_registry.register(
    name="bon_nom_document_en_contexte_4",
    description="Vérifie si le nom du document en contexte (position 4) correspond à celui attendu",
    metric_type="llm",
    require=["nom_document_reponse_bot_4", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte_4(output, output_true, **kwargs):
    nom_document_reponse_bot = kwargs.get("nom_document_reponse_bot_4", "")
    nom_document_verite_terrain = kwargs.get("nom_document_verite_terrain", "")
    return _compare_documents(nom_document_reponse_bot, nom_document_verite_terrain)
