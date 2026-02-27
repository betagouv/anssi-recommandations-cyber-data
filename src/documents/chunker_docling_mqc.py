from pathlib import Path
from typing import NamedTuple, Type

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import BaseChunk

from documents.chunker_docling import ChunkerDocling, TypeFichier
from documents.document import Document
from documents.extrais_les_chunks import extrais_les_chunks
from documents.filtre_resultat import filtre_les_resultats
from documents.indexeur import DocumentAIndexer


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


class ChunkerDoclingMQC(ChunkerDocling):
    def __init__(self, converter: Type[DocumentConverter] = DocumentConverter):
        super().__init__(converter)
        self.type_fichier = TypeFichier.TEXTE

    def _cree_le_document(
        self, resultat_conversion: ConversionResult, document: DocumentAIndexer
    ) -> Document:
        self.nom_fichier = Path(document.chemin).name.replace(".pdf", ".txt")
        elements_filtres = filtre_les_resultats(resultat_conversion)
        chunks = extrais_les_chunks(elements_filtres)

        return self.__extrais_le_document(chunks, document)

    def __extrais_le_document(
        self, chunks: list[BaseChunk], document_a_indexer: DocumentAIndexer
    ) -> Document:
        document = Document(document_a_indexer.nom_document, document_a_indexer.url)

        for chunk in chunks:
            try:
                document.ajoute(document_a_indexer.generateur.genere(chunk))
            except Exception:
                continue

        return document
