from typing import cast, NamedTuple

from docling.datamodel.document import ConversionResult
from docling_core.transforms.chunker import BaseChunk, DocMeta

from guides.chunker_docling import ChunkerDocling, extrait_position
from guides.extrais_les_chunks import extrais_les_chunks
from guides.filtre_resultat import filtre_les_resultats
from guides.guide import Guide


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


class ChunkerDoclingMQC(ChunkerDocling):
    def _convertis_en_blocs_de_pages(self, result: ConversionResult) -> Guide:
        elements_filtres = filtre_les_resultats(result)
        chunks = extrais_les_chunks(elements_filtres)

        return self.__extrais_le_guide(chunks)

    def __extrais_le_guide(self, chunks: list[BaseChunk]) -> Guide:
        guide = Guide()

        for chunk in chunks:
            try:
                numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                position = extrait_position(chunk)
                guide.ajoute_bloc_a_la_page(numero_page, position, chunk.text)
            except Exception:
                continue

        return guide
