from docling_core.transforms.chunker import BaseChunk, DocMeta

from documents.elements_filtres import ElementsFiltres
from documents.pdf.categorise_le_contenu import ajoute_la_categorisation_du_contenu


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
