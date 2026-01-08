import pytest
from docling_core.transforms.chunker import BaseChunk, DocMeta
from docling_core.types.doc import BoundingBox
from docling_core.types.doc import TextItem, DocItemLabel
from docling_core.types.doc.document import ProvenanceItem

from guides.extrais_les_chunks import extrais_les_chunks


@pytest.fixture
def cree_chunk_avec_page():
    def _cree_chunk_avec_page(texte: str, numero_page: int) -> BaseChunk:
        bbox = BoundingBox(l=100.0, t=200.0, r=300.0, b=400.0)
        prov = ProvenanceItem(page_no=numero_page, bbox=bbox, charspan=(0, len(texte)))
        doc_item = TextItem(
            text=texte,
            label=DocItemLabel.TEXT,
            self_ref=f"#/test/{numero_page}",
            orig=texte,
            prov=[prov],
        )
        meta = DocMeta(doc_items=[doc_item])
        return BaseChunk(text=texte, meta=meta)

    return _cree_chunk_avec_page


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
