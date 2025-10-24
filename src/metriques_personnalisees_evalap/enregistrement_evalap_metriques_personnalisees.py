from . import metric_registry  # type: ignore[attr-defined]
from evalap.api.metrics.metriques_personnalisees import (  # type: ignore[import-not-found, import-untyped]
    _metrique_bon_nom_document_en_contexte,
)


def _creer_fonction_metrique(position: int):
    def metrique(output, output_true, nom_document_verite_terrain: str = "", **kwargs):
        nom_document_reponse_bot = kwargs.get(
            f"nom_document_reponse_bot_{position}", ""
        )
        return _metrique_bon_nom_document_en_contexte(
            nom_document_reponse_bot, nom_document_verite_terrain
        )

    return metrique


positions = [
    "premier",
    "second",
    "troisième",
    "quatrième",
    "cinquième",
]

for position, ordinal in enumerate(positions):
    metric_registry.register(
        name=f"bon_nom_document_en_contexte_{position}",
        description=f"Vérifie si le nom du document du {ordinal} paragraphe, retourné par le système RAG correspond à celui attendu",
        metric_type="llm",
        require=[f"nom_document_reponse_bot_{position}", "nom_document_verite_terrain"],
    )(_creer_fonction_metrique(position))
