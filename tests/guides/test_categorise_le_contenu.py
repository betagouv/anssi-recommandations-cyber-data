import pytest
from docling_core.types.doc import (
    TextItem,
    DocItemLabel,
    SectionHeaderItem,
    TableItem,
    TableData,
    TableCell,
    ProvenanceItem,
    BoundingBox,
    CoordOrigin,
)

from guides.categorise_le_contenu import ajoute_la_categorisation_du_contenu


@pytest.mark.parametrize(
    "_description, item, attendu",
    [
        (
            "[RECOMMANDATION] Recommandation 1",
            TextItem(text="R1", label=DocItemLabel.TEXT, self_ref="#/test/42", orig=""),
            "[RECOMMANDATION] R1",
        ),
        (
            "[RECOMMANDATION] Recommandation 18",
            TextItem(
                text="R18", label=DocItemLabel.TEXT, self_ref="#/test/42", orig=""
            ),
            "[RECOMMANDATION] R18",
        ),
        (
            "[TEXTE] Texte lisible",
            TextItem(
                text="Hello world",
                label=DocItemLabel.TEXT,
                self_ref="#/test/42",
                orig="",
            ),
            "[TEXTE] Hello world",
        ),
        (
            "[NOTE] Note lisible",
            TextItem(
                text="Hello world",
                label=DocItemLabel.FOOTNOTE,
                self_ref="#/test/42",
                orig="",
            ),
            "[NOTE] Hello world",
        ),
    ],
)
def test_categorise_le_contenu_pour_les_textes_items(_description, item, attendu):
    resultat = ajoute_la_categorisation_du_contenu(item)

    assert resultat == attendu


@pytest.mark.parametrize(
    "_description, item, attendu",
    [
        (
            "[RECOMMANDATION] Recommandation 1",
            SectionHeaderItem(
                text="R1",
                label=DocItemLabel.SECTION_HEADER,
                self_ref="#/test/42",
                orig="",
            ),
            "[RECOMMANDATION] R1",
        ),
        (
            "[RECOMMANDATION] Recommandation 18",
            SectionHeaderItem(
                text="R18",
                label=DocItemLabel.SECTION_HEADER,
                self_ref="#/test/42",
                orig="",
            ),
            "[RECOMMANDATION] R18",
        ),
        (
            "[SECTION] Texte lisible",
            SectionHeaderItem(
                text="1.2 Hello world",
                label=DocItemLabel.SECTION_HEADER,
                self_ref="#/test/42",
                orig="",
            ),
            "[SECTION] 1.2 Hello world",
        ),
        (
            "[SOUS-TITRE] Note lisible",
            SectionHeaderItem(
                text="Hello world",
                label=DocItemLabel.SECTION_HEADER,
                self_ref="#/test/42",
                orig="",
            ),
            "[SOUS-TITRE] Hello world",
        ),
    ],
)
def test_categorise_le_contenu_pour_les_entetes(_description, item, attendu):
    resultat = ajoute_la_categorisation_du_contenu(item)

    assert resultat == attendu


def test_categorise_le_contenu_pour_les_tableaux():
    table = TableItem(
        self_ref="#/test/42",
        data=TableData(
            num_cols=1,
            num_rows=1,
            table_cells=[
                TableCell(
                    text="Tableau exemple",
                    start_row_offset_idx=0,
                    end_row_offset_idx=1,
                    start_col_offset_idx=0,
                    end_col_offset_idx=1,
                    column_header=True,
                )
            ],
        ),
    )
    resultat = ajoute_la_categorisation_du_contenu(table)

    assert (
        resultat
        == """[TABLEAU]
| Tableau exemple |
| --- |"""
    )


def test_categorise_le_contenu_pour_les_tableaux_avec_plusieurs_cellules():
    table = TableItem(
        self_ref="#/test/42",
        prov=[
            ProvenanceItem(
                page_no=1,
                bbox=BoundingBox(
                    l=70.24855041503906,
                    t=628.8914947509766,
                    r=550.4656982421875,
                    b=484.9783630371094,
                    coord_origin=CoordOrigin.BOTTOMLEFT,
                ),
                charspan=(0, 0),
            )
        ],
        data=TableData(
            num_cols=2,
            num_rows=3,
            table_cells=[
                TableCell(
                    text="Colonne 1",
                    start_row_offset_idx=0,
                    end_row_offset_idx=1,
                    start_col_offset_idx=0,
                    end_col_offset_idx=1,
                    column_header=True,
                ),
                TableCell(
                    text="Colonne 2",
                    start_row_offset_idx=0,
                    end_row_offset_idx=1,
                    start_col_offset_idx=1,
                    end_col_offset_idx=2,
                    column_header=True,
                ),
                TableCell(
                    text="Ligne 1, Colonne 1",
                    start_row_offset_idx=1,
                    end_row_offset_idx=2,
                    start_col_offset_idx=0,
                    end_col_offset_idx=1,
                    column_header=False,
                ),
                TableCell(
                    text="Ligne 1, Colonne 2",
                    start_row_offset_idx=1,
                    end_row_offset_idx=2,
                    start_col_offset_idx=1,
                    end_col_offset_idx=2,
                    column_header=False,
                ),
                TableCell(
                    text="Ligne 2, Colonne 1",
                    start_row_offset_idx=2,
                    end_row_offset_idx=3,
                    start_col_offset_idx=0,
                    end_col_offset_idx=1,
                    column_header=False,
                ),
                TableCell(
                    text="Ligne 2, Colonne 2",
                    start_row_offset_idx=2,
                    end_row_offset_idx=3,
                    start_col_offset_idx=1,
                    end_col_offset_idx=2,
                    column_header=False,
                ),
            ],
        ),
    )
    resultat = ajoute_la_categorisation_du_contenu(table)

    assert (
        resultat
        == """[TABLEAU]
| Colonne 1 | Colonne 2 |
| --- | --- |
| Ligne 1, Colonne 1 | Ligne 1, Colonne 2 |
| Ligne 2, Colonne 1 | Ligne 2, Colonne 2 |"""
    )
