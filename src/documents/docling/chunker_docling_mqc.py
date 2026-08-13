from pathlib import Path
from typing import Callable, Type

from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter

from documents.docling.chunker_docling import ChunkerDocling, TypeFichier
from documents.docling.document import Document
from documents.docling.filtre_resultat import filtre_les_resultats
from documents.pdf.assembleur_blocs_json import AssembleurDeBlocsJson
from documents.pdf.convertisseur_ocr_json import (
    ExtracteurDeBlocsOcr,
    ExtracteurDeBlocsOcrDepuisUnPdf,
)
from documents.pdf.document_pdf import BlocPagePDF, PagePDF
from documents.page import ContexteDuBloc, Page
from documents.pdf.pages_avec_texte import (
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
        convertisseur_ocr_json: ExtracteurDeBlocsOcr | None = None,
    ):
        super().__init__(
            converter,
            cle_api,
            url_albert,
        )
        self.type_fichier = TypeFichier.TEXTE
        self.identifie_les_plages_de_pages_pdf = identifie_les_plages_de_pages_pdf
        self.convertisseur_ocr_json = convertisseur_ocr_json or ExtracteurDeBlocsOcrDepuisUnPdf(
            cle_api=cle_api,
            url_albert=url_albert,
        )

    def applique(self, document: DocumentAIndexer) -> Document:
        if document.type == "PDF":
            return self._applique_le_pdf_avec_ocr_json(document)
        return super().applique(document)

    def _applique_le_pdf_avec_ocr_json(
        self,
        document_a_indexer: DocumentAIndexer,
    ) -> Document:
        plages_de_pages_avec_du_contenu = (
            self.identifie_les_plages_de_pages_pdf(str(document_a_indexer.chemin))
        )
        document = Document(document_a_indexer)
        self.nom_fichier = (
            Path(document_a_indexer.chemin)
            .name.replace(".pdf", ".txt")
            .replace(".html", ".txt")
        )
        if plages_de_pages_avec_du_contenu == []:
            document.pages = {1: PagePDF(1)}
            return document

        resultat_ocr = self.convertisseur_ocr_json.convertit(
            document_a_indexer.chemin,
            plages_de_pages_avec_du_contenu,
        )
        document.erreurs_pages = resultat_ocr.erreurs
        blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)
        pages: dict[int, Page] = {
            numero_page: PagePDF(numero_page)
            for numero_page in range(1, resultat_ocr.nombre_de_pages + 1)
        }
        for bloc_indexable in blocs_indexables:
            page = pages.setdefault(
                bloc_indexable.page_debut,
                PagePDF(bloc_indexable.page_debut),
            )
            page.ajoute_bloc(
                BlocPagePDF(
                    texte=bloc_indexable.texte,
                    numero_page=bloc_indexable.page_debut,
                    position_page=len(page.blocs),
                    derniere_page=bloc_indexable.page_fin,
                    pages=bloc_indexable.pages_couvertes,
                    contexte=ContexteDuBloc(
                        type_de_bloc=bloc_indexable.contexte.type_de_bloc,
                        code_recommandation=bloc_indexable.contexte.code_recommandation,
                        titre=bloc_indexable.contexte.titre,
                        section=bloc_indexable.contexte.section,
                        chemin_des_sections=bloc_indexable.contexte.chemin_des_sections,
                        niveau=bloc_indexable.contexte.niveau,
                    ),
                )
            )
        document.pages = pages
        return document

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
