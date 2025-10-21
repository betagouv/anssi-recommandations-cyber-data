from . import metric_registry  # type: ignore[attr-defined]
from evalap.api.metrics.metriques_personnalisees import (  # type: ignore[import-not-found, import-untyped]
    _metrique_bon_nom_document_en_contexte,
)


@metric_registry.register(
    name="bon_nom_document_en_contexte",
    description="Vérifie si le nom du document retourné par le système RAG correspond à celui attendu",
    metric_type="llm",  # paramètre trompeur mais c'est bien le type pour une métrique personnalisée non llm ...
    require=["nom_document_reponse_bot", "nom_document_verite_terrain"],
)
def metrique_bon_nom_document_en_contexte(  # type: ignore[no-redef]
    output,
    output_true,
    nom_document_reponse_bot: str = "",
    nom_document_verite_terrain: str = "",
    **_,
):
    return _metrique_bon_nom_document_en_contexte(
        nom_document_reponse_bot, nom_document_verite_terrain
    )
