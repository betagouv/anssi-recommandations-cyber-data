from deepeval.metrics.faithfulness.schema import Truths
from evaluation.client_deepeval_albert import ClientDeepEvalAlbert


class ClientDeepEvalAlbertDeTest(ClientDeepEvalAlbert):
    def _appel_api_albert(self, prompt: str) -> str:
        return '```json\n{"truths": ["Internet does not provide.","Data sent via email or online hosting tools (Cloud).","The secret (password, key, etc.).","Frequent professional movements.","Sensitive data.","A secret.","It is advisable.","When a service [\[CRYPTO\\_B1\].](#page-51-0).","When a service [\[CRYPTO\\_B1\].](#page-51-0).","The service.", "The logging system [\[NT\\_JOURNAL\].](#page-52-0)", "chapitre 3.2 de [\\\[NT\\_JOURNAL\\].](#page-52-0)"]}\n```'


def test_verifie_la_reponse_au_format_json_albert():
    generation = ClientDeepEvalAlbertDeTest().generate("A prompt", Truths)

    assert generation.truths == [
        "Internet does not provide.",
        "Data sent via email or online hosting tools (Cloud).",
        "The secret (password, key, etc.).",
        "Frequent professional movements.",
        "Sensitive data.",
        "A secret.",
        "It is advisable.",
        "When a service [\\[CRYPTO\\_B1\\].](#page-51-0).",
        "When a service [\\[CRYPTO\\_B1\\].](#page-51-0).",
        "The service.",
        "The logging system [\\[NT\\_JOURNAL\\].](#page-52-0)",
        "chapitre 3.2 de [\\[NT\\_JOURNAL\\].](#page-52-0)",
    ]
