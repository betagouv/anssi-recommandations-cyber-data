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

from documents.categorise_le_contenu import ajoute_la_categorisation_du_contenu

type ElementsFiltres = list[
    TitleItem
    | SectionHeaderItem
    | ListItem
    | CodeItem
    | FormulaItem
    | TextItem
    | TableItem
]


def extrais_les_chunks(
    elements_filtres: ElementsFiltres,
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
