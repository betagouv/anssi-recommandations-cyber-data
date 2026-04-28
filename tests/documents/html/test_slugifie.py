import pytest

from documents.html.slugifie import slugifie


@pytest.mark.parametrize(
    "texte,attendu",
    [
        ("Atelier Photo 2026", "atelier-photo-2026"),
        ("éàü", "eau"),
        ("  multiple   espaces  ", "multiple-espaces"),
        ("", ""),
    ],
)
def test_slugifie_normalise_le_texte(texte, attendu):
    assert slugifie(texte) == attendu


@pytest.mark.parametrize(
    "texte",
    [
        "une question tres longue " * 20,
        "a" * 1000,
    ],
)
def test_slugifie_tronque_a_250_caracteres_au_maximum(texte):
    assert len(slugifie(texte)) <= 250
