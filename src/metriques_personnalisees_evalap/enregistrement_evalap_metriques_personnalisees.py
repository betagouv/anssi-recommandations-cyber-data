from . import metric_registry  # type: ignore[attr-defined]
from evalap.api.metrics.metriques_personnalisees import (  # type: ignore[import-not-found, import-untyped]
    _metrique_bon_nom_document_en_contexte,
    _metrique_bon_numero_page_en_contexte,
    _metrique_score_numero_page_en_contexte,
)


positions = [
    "premier",
    "second",
    "troisième",
    "quatrième",
    "cinquième",
]


def _enregistre_metriques_par_position(
    nom_base: str,
    description_template: str,
    fonction_metrique,
    param_bot: str,
    param_verite: str,
    valeur_defaut=None,
):
    def _creer_fonction(position: int):
        def metrique(output, output_true, **kwargs):
            param_verite_value = kwargs.get(param_verite, valeur_defaut)
            param_bot_value = kwargs.get(f"{param_bot}_{position}", valeur_defaut)
            return fonction_metrique(param_bot_value, param_verite_value)

        return metrique

    for position, ordinal in enumerate(positions):
        metric_registry.register(
            name=f"{nom_base}_{position}",
            description=description_template.format(ordinal=ordinal),
            metric_type="llm",
            require=[f"{param_bot}_{position}", param_verite],
        )(_creer_fonction(position))


_enregistre_metriques_par_position(
    "bon_nom_document_en_contexte",
    "Vérifie si le nom du document du {ordinal} paragraphe, retourné par le système RAG correspond à celui attendu",
    _metrique_bon_nom_document_en_contexte,
    "nom_document_reponse_bot",
    "nom_document_verite_terrain",
    "",
)

_enregistre_metriques_par_position(
    "score_numero_page_en_contexte",
    "Calcule un score entre le numéro de page attendu et le numéro de page du {ordinal} paragraphe retourné par le système RAG.",
    _metrique_score_numero_page_en_contexte,
    "numero_page_reponse_bot",
    "numero_page_verite_terrain",
    None,
)

_enregistre_metriques_par_position(
    "bon_numero_page_en_contexte",
    "Vérifie si le numéro de page attendu est identique au numéro de page du {ordinal} paragraphe retourné par le système RAG.",
    _metrique_bon_numero_page_en_contexte,
    "numero_page_reponse_bot",
    "numero_page_verite_terrain",
    None,
)
