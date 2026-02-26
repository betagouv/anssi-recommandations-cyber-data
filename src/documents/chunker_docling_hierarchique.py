from pathlib import Path
from typing import cast

from docling.datamodel.document import ConversionResult
from docling_core.transforms.chunker import HierarchicalChunker, DocMeta

from documents.chunker_docling import ChunkerDocling
from documents.chunker_docling import extrais_position
from documents.document import Document
from documents.indexeur import DocumentPDF


class ChunkerDoclingHierarchique(ChunkerDocling):
    def _cree_le_document(
        self, resultat_conversion: ConversionResult, document_pdf: DocumentPDF
    ) -> Document:
        self.nom_fichier = Path(document_pdf.chemin_pdf).name
        chunker = HierarchicalChunker()

        def est_lisible(text: str) -> bool:
            if not text:
                return False

            alpha = sum(c.isalpha() for c in text)
            ratio = alpha / max(len(text), 1)

            return ratio > 0.5 and " " in text

        document = Document(document_pdf)

        for index, chunk in enumerate(chunker.chunk(resultat_conversion.document)):
            if est_lisible(chunk.text):
                numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                document.ajoute_bloc_a_la_page(
                    numero_page=numero_page,
                    position=extrais_position(chunk),
                    texte=chunk.text,
                )
        return document
