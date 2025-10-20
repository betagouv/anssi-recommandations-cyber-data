from . import metric_registry  # type: ignore[attr-defined]


@metric_registry.register(
    name="exact_match",
    description="Metrique de test ",
    metric_type="llm",
    require=["output", "output_true"],
)
def metrique_correspondance_exacte(output, output_true, **kwargs):
    sortie_normalisee = output.strip().lower()
    attendu_normalise = output_true.strip().lower()

    score = 1.0 if sortie_normalisee == attendu_normalise else 0.0

    if score == 1.0:
        observation = "Correspondance exacte trouvée"
    else:
        observation = (
            f"Aucune correspondance : attendu '{output_true}' mais obtenu '{output}'"
        )

    return score, observation
