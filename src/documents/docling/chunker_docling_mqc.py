from pathlib import Path
from typing import Type

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter

from documents.docling.chunker_docling import ChunkerDocling, TypeFichier
from documents.docling.document import Document
from documents.docling.filtre_resultat import filtre_les_resultats
from documents.indexeur.indexeur import DocumentAIndexer


class ChunkerDoclingMQC(ChunkerDocling):
    def __init__(
        self,
        converter: Type[DocumentConverter] = DocumentConverter,
        cle_api: str = "",
        url_albert: str = "https://albert.api.etalab.gouv.fr/v1",
    ):
        super().__init__(converter, cle_api, url_albert)
        self.type_fichier = TypeFichier.TEXTE

    def _cree_le_document(
        self,
        resultat_conversion: ConversionResult,
        document_a_indexer: DocumentAIndexer,
    ) -> Document:
        self.nom_fichier = (
            Path(document_a_indexer.chemin)
            .name.replace(".pdf", ".txt")
            .replace(".html", ".txt")
        )
        elements_filtres = filtre_les_resultats(resultat_conversion)
        document = Document(document_a_indexer)
        document.genere_les_pages(
            document_a_indexer.generateur,
            elements_filtres,
            resultat_conversion.document,
        )
        return document
