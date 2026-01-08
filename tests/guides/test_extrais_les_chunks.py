from docling_core.types.doc import TextItem, DocItemLabel

from guides.extrais_les_chunks import extrais_les_chunks


def test_extrais_tous_les_chunks():
    texte_1 = TextItem(
        text="Hello world",
        label=DocItemLabel.TEXT,
        self_ref="#/test/42",
        orig="",
    )
    texte_2 = TextItem(
        text="Bonjour le monde",
        label=DocItemLabel.TEXT,
        self_ref="#/test/42",
        orig="",
    )
    pied_de_page = TextItem(
        text="Pied de page",
        label=DocItemLabel.FOOTNOTE,
        self_ref="#/test/42",
        orig="",
    )
    texte_3 = TextItem(
        text="Un nouveau texte",
        label=DocItemLabel.TEXT,
        self_ref="#/test/42",
        orig="",
    )

    chunks = extrais_les_chunks([texte_1, texte_2, pied_de_page, texte_3])

    assert len(chunks) == 4
    assert chunks[0].text == "[TEXTE] Hello world"
    assert chunks[1].text == "[TEXTE] Bonjour le monde"
    assert chunks[2].text == "[NOTE] Pied de page"
    assert chunks[3].text == "[TEXTE] Un nouveau texte"
