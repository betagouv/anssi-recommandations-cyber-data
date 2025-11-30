from deepeval.test_case import LLMTestCase

from evaluation.metriques_personnalisees.de_deepeval.metrique_bon_nom_document import (
    MetriqueBonNomDocument,
)
from infra.evaluateur.deep_eval.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)


def test_evalue_un_cas_de_test():
    import multiprocessing as mp

    mp.set_start_method("spawn", force=True)
    cas_de_test = LLMTestCase(
        input="Qu'elle est la bonne longueur d'un mot de passe?",
        actual_output="réponse mqc",
        expected_output="réponse envisagée",
        retrieval_context=["test"],
        context=["test"],
        additional_metadata={
            "numero_ligne": 0,
            "nom_document_reponse_bot_0": "document_test",
            "nom_document_verite_terrain_0": "document_test",
        },
    )
    metriques = MetriqueBonNomDocument(
        "nom_document_reponse_bot_0", "nom_document_verite_terrain_0"
    )

    resultats = EvaluateurDeepevalMultiProcessus().evaluate([cas_de_test], [metriques])

    assert len(resultats) == 1
