from docling_core.transforms.chunker import BaseChunk, DocMeta
from docling_core.types.doc import (
    TitleItem,
    SectionHeaderItem,
    ListItem,
    CodeItem,
    FormulaItem,
    TextItem,
    TableItem,
)

from guides.categorise_le_contenu import ajoute_la_categorisation_du_contenu


def extrais_les_chunks(
    elements_filtres: list[
        TitleItem
        | SectionHeaderItem
        | ListItem
        | CodeItem
        | FormulaItem
        | TextItem
        | TableItem
    ],
) -> list[BaseChunk]:
    return list(
        map(
            lambda element: BaseChunk(
                text=ajoute_la_categorisation_du_contenu(element),
                meta=DocMeta(doc_items=[element]),
            ),
            elements_filtres,
        )
    )
