from pathlib import Path
from typing import cast, NamedTuple, Type

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import BaseChunk, DocMeta

from guides.chunker_docling import ChunkerDocling, extrais_position, TypeFichier
from guides.extrais_les_chunks import extrais_les_chunks
from guides.filtre_resultat import filtre_les_resultats
from guides.guide import Guide
from guides.indexeur import DocumentPDF


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


class ChunkerDoclingMQC(ChunkerDocling):
    def __init__(self, converter: Type[DocumentConverter] = DocumentConverter):
        super().__init__(converter)
        self.type_fichier = TypeFichier.TEXTE

    def _cree_le_guide(
        self, resultat_conversion: ConversionResult, document: DocumentPDF
    ) -> Guide:
        self.nom_fichier = Path(document.chemin_pdf).name.replace(".pdf", ".txt")
        elements_filtres = filtre_les_resultats(resultat_conversion)
        chunks = extrais_les_chunks(elements_filtres)

        return self.__extrais_le_guide(chunks, document)

    def __extrais_le_guide(
        self, chunks: list[BaseChunk], document: DocumentPDF
    ) -> Guide:
        guide = Guide(document)

        for chunk in chunks:
            try:
                numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                position = extrais_position(chunk)
                guide.ajoute_bloc_a_la_page(numero_page, position, chunk.text)
            except Exception:
                continue

        return guide
