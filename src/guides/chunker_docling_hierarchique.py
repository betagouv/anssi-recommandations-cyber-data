from typing import cast

from docling.datamodel.document import ConversionResult
from docling_core.transforms.chunker import HierarchicalChunker, DocMeta

from guides.chunker_docling import ChunkerDocling
from guides.chunker_docling import extrais_position
from guides.guide import Guide


class ChunkerDoclingHierarchique(ChunkerDocling):
    def _cree_le_guide(self, result: ConversionResult) -> Guide:
        chunker = HierarchicalChunker()

        def est_lisible(text: str) -> bool:
            if not text:
                return False

            alpha = sum(c.isalpha() for c in text)
            ratio = alpha / max(len(text), 1)

            return ratio > 0.5 and " " in text

        guide = Guide()

        for index, chunk in enumerate(chunker.chunk(result.document)):
            if est_lisible(chunk.text):
                numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                guide.ajoute_bloc_a_la_page(
                    numero_page=numero_page,
                    position=extrais_position(chunk),
                    texte=chunk.text,
                )
        return guide
