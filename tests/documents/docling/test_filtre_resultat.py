from pathlib import Path

import pytest
from docling.backend.pdf_backend import PdfDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling.document_converter import ConversionResult
from docling_core.types import DoclingDocument
from docling_core.types.doc import TextItem, DocItemLabel, TableItem, TableData

from docling_core.types.doc import GroupItem, RefItem

from documents.docling.filtre_resultat import filtre_les_resultats


def _creer_document(texts=None, tables=None):
    body_ref = RefItem(**{"$ref": "#/body"})
    texts = [
        t.model_copy(update={"self_ref": f"#/texts/{i}", "parent": body_ref})
        for i, t in enumerate(texts or [])
    ]
    tables = [
        t.model_copy(update={"self_ref": f"#/tables/{i}", "parent": body_ref})
        for i, t in enumerate(tables or [])
    ]
    children = [RefItem(**{"$ref": item.self_ref}) for item in texts + tables]
    body = GroupItem(name="_root_", self_ref="#/body", children=children)
    return DoclingDocument(name="", texts=texts, tables=tables, body=body)


@pytest.mark.parametrize(
    "_description, texte",
    [
        ("Recommandation 1", "R1"),
        ("Recommandation 18", "R18"),
        ("Texte lisible", "Hello world"),
        (
            "Phrase lisible",
            "Ceci est une phrase avec suffisamment de mots",
        ),
        ("Alpha", "abc"),
        ("Avec une ligature", "œuvre"),
    ],
)
def test_est_lisible(_description, texte):
    text = TextItem(text=texte, label=DocItemLabel.TEXT, self_ref="#/test/42", orig="")
    resultats = filtre_les_resultats(
        ConversionResult(
            document=_creer_document(texts=[text]),
            input=InputDocument(
                format=InputFormat.PDF,
                backend=PdfDocumentBackend,
                path_or_stream=Path(),
            ),
        )
    )

    assert any(r.text == texte for r in resultats)


@pytest.mark.parametrize(
    "_description, texte",
    [
        ("Pas de texte", ""),
        ("Chaine vide", "   "),
        ("Bruit court", ".."),
        ("Points successifs", "...."),
        ("Numérique avec point et espace", "12. 34"),
        ("Numérique avec espace et tiret", "12 -"),
        (
            "Données de document inintéressantes",
            "Version 1.0 - 29/04/2024 - ANSSI-PA-102",
        ),
        ("Numéro de référence quelconque", "978-2-11-167157-7"),
        ("Date", "Avril 2024"),
        ("Ratio alpha", "ab12 cd34 ef56"),
    ],
)
def test_n_est_pas_lisible(_description, texte):
    text = TextItem(text=texte, label=DocItemLabel.TEXT, self_ref="#/test/42", orig="")
    resultats = filtre_les_resultats(
        ConversionResult(
            document=_creer_document(texts=[text]),
            input=InputDocument(
                format=InputFormat.PDF,
                backend=PdfDocumentBackend,
                path_or_stream=Path(),
            ),
        )
    )

    assert not any(r.text == texte for r in resultats)


def test_ajoute_les_tableaux():
    tableau = TableItem(
        data=TableData(), label=DocItemLabel.TABLE, self_ref="#/test/42"
    )
    resultats = filtre_les_resultats(
        ConversionResult(
            document=_creer_document(tables=[tableau]),
            input=InputDocument(
                format=InputFormat.PDF,
                backend=PdfDocumentBackend,
                path_or_stream=Path(),
            ),
        )
    )

    assert len(resultats) == 1 and isinstance(resultats[0], TableItem)
