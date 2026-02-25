from types import SimpleNamespace

import pytest

from guides.generateur_question.producteur_questions import (
    ProducteurQuestionsOpenAI,
    _charge_prompt_systeme,
    calcule_nombre_questions,
    parse_questions_depuis_contenu,
)
from guides.generateur_question.compteurs_thematique import (
    CompteurThematiques,
    CompteursThematique,
)
from guides.generateur_question.utils import (
    _extrait_objet_json,
    _compte_mots,
    _compte_phrases,
)


class FauxClientOpenAI:
    def __init__(self, contenu: str):
        self.contenu = contenu
        self.appels: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._cree))

    def _cree(self, **kwargs):
        self.appels.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.contenu))]
        )


def test_producteur_questions_openai_retourne_les_questions_json():
    contenu = """```json
                {"questions": ["Question 1 ?", "Question 2 ?"]}
                ```"""
    client = FauxClientOpenAI(contenu)
    producteur = ProducteurQuestionsOpenAI(
        client=client,
        modele_generation="modele-test",
    )

    paragraphe = "Un paragraphe test simple."
    resultats = producteur(paragraphe)

    assert resultats == ["Question 1 ?", "Question 2 ?"]
    assert len(client.appels) == 1
    assert client.appels[0]["model"] == "modele-test"


def test_charge_prompt_systeme_charge_le_contenu_du_fichier():
    prompt = _charge_prompt_systeme()
    assert "Tu es un composant de génération de questions" in prompt


def test_extrait_objet_json_retire_les_fences():
    contenu = '```json\n{"questions": ["Q1 ?"]}\n```'

    extrait = _extrait_objet_json(contenu)

    assert extrait == '{"questions": ["Q1 ?"]}'


def test_parse_questions_depuis_contenu_extrait_les_questions():
    contenu = '```json\n{"questions": ["Q1 ?", "Q2 ?"]}\n```'

    resultats = parse_questions_depuis_contenu(contenu)

    assert resultats == ["Q1 ?", "Q2 ?"]


def test_compte_mots_compte_les_mots():
    assert _compte_mots("Un texte simple.") == 3


def test_compte_phrases_compte__une_phrase():
    assert _compte_phrases("Une première phrase.") == 1


def test_compte_phrases_compte_au_moins_une_phrase():
    assert _compte_phrases("") == 1


def test_compte_phrases_compte_les_phrases():
    assert _compte_phrases("Phrase une. Phrase deux ? Phrase trois !") == 3


class CompteurThematiquesDeTest(CompteurThematiques):
    def __init__(self, topics: int):
        self.topics = topics

    def nombre_topics(self, _: str) -> int:
        return self.topics


@pytest.mark.parametrize(
    ("topics", "attendu"),
    [
        (0, 0),
        (1, 3),
        (2, 3),
        (5, 5),
        (10, 10),
        (12, 10),
    ],
)
def test_calcule_nombre_questions_est_borne(topics: int, attendu: int):
    compteur = CompteurThematiquesDeTest(topics)
    resultat = calcule_nombre_questions("peu importe", compteur_thematiques=compteur)
    assert resultat == attendu


def test_compteur_topics_retourne_0_si_paragraphe_vide():
    compteur = CompteursThematique()
    assert compteur.nombre_topics("") == 0


def test_compteur_topics_retourne_1_si_pas_assez_de_phrases():
    compteur = CompteursThematique()
    assert compteur.nombre_topics("Une seule phrase.") == 1
