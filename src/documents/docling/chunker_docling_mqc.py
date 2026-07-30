from pathlib import Path
from typing import Callable, Type

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter

from documents.docling.chunker_docling import ChunkerDocling, TypeFichier
from documents.docling.document import Document
from documents.docling.filtre_resultat import filtre_les_resultats
from documents.docling.pages_avec_texte import (
    identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte,
)
from documents.indexeur.indexeur import DocumentAIndexer


class ChunkerDoclingMQC(ChunkerDocling):
    def __init__(
        self,
        converter: Type[DocumentConverter] = DocumentConverter,
        cle_api: str = "",
        url_albert: str = "https://albert.api.etalab.gouv.fr/v1",
        identifie_les_plages_de_pages_pdf: Callable[
            [str], list[tuple[int, int]] | None
        ] = identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte,
    ):
        super().__init__(
            converter,
            cle_api,
            url_albert,
            identifie_les_plages_de_pages_pdf,
        )
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
