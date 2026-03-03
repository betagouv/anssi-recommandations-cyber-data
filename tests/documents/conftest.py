import json
import sys
from pathlib import Path
from typing import Callable, Type, Union, Optional

import pytest
from docling.backend.pdf_backend import PdfDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling.datamodel.settings import PageRange
from docling.document_converter import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.types import DoclingDocument
from docling_core.types.doc import (
    BoundingBox,
    ProvenanceItem,
    TextItem,
    DocItemLabel,
    SectionHeaderItem,
    TableItem,
    TableData,
    TableCell,
)
from docling_core.types.io import DocumentStream

from documents.chunker_docling import TypeFichier
from documents.chunker_docling_mqc import ChunkerDoclingMQC
from documents.document import Document
from documents.extrais_les_chunks import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.indexeur import (
    ReponseDocument,
    ReponseDocumentEnSucces,
    DocumentAIndexer,
)
from documents.page import Position, PagePDF, BlocPagePDF, Page


@pytest.fixture
def fichier_pdf(tmp_path) -> Callable[[str], Path]:
    def _cree_fichier_pdf(nom: str) -> Path:
        le_fichier = (tmp_path / nom).with_suffix(".pdf")
        with open(le_fichier, "wb") as f:
            f.write(b"pdf content")
        return le_fichier

    return _cree_fichier_pdf


@pytest.fixture
def dossier_guide_anssi(tmp_path, fichier_pdf) -> Path:
    return fichier_pdf("test.pdf").parent


@pytest.fixture
def fichier_urls_specifiques(tmp_path) -> Path:
    contenu = {"test.pdf": "https://url_de_test.com"}

    chemin_fichier = tmp_path / "urls_specifiques.json"
    chemin_fichier.write_text(json.dumps(contenu), encoding="utf-8")

    return chemin_fichier


@pytest.fixture
def une_reponse_document() -> ReponseDocument:
    return ReponseDocumentEnSucces(
        id="doc123",
        name="test.pdf",
        collection_id="12345",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )


@pytest.fixture
def une_reponse_document_parametree() -> Callable[[str, str], ReponseDocument]:
    def _une_reponse_document_parametree(
        id_document: str, nom_document: str
    ) -> ReponseDocument:
        return ReponseDocumentEnSucces(
            id=id_document,
            name=nom_document,
            collection_id="12345",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

    return _une_reponse_document_parametree


@pytest.fixture
def un_convertisseur_avec_un_texte() -> Callable[[], Type[DocumentConverter]]:
    class ConverterDeTest(DocumentConverter):
        def convert(
            self,
            document: Union[Path, str, DocumentStream],  # TODO review naming
            headers: Optional[dict[str, str]] = None,
            raises_on_error: bool = True,
            max_num_pages: int = sys.maxsize,
            max_file_size: int = sys.maxsize,
            page_range: PageRange = (1, 1),
        ) -> ConversionResult:
            texte = "Un texte"
            bbox = BoundingBox(l=100.0, t=200.0, r=300.0, b=400.0)
            prov = ProvenanceItem(page_no=1, bbox=bbox, charspan=(0, len(texte)))
            text = TextItem(
                text=texte,
                label=DocItemLabel.TEXT,
                self_ref="#/test/42",
                orig="",
                prov=[prov],
            )
            return ConversionResult(
                document=DoclingDocument(name="", texts=[text]),
                input=InputDocument(
                    format=InputFormat.PDF,
                    backend=PdfDocumentBackend,  # type: ignore[type-abstract]
                    path_or_stream=Path(),
                ),
            )

    def _convertisseur() -> Type[DocumentConverter]:
        return ConverterDeTest

    return _convertisseur


class ConstructeurDeTextItem:
    def __init__(self):
        super().__init__()
        self.texte = "Un texte"
        self.bounding_box = BoundingBox(l=100.0, t=200.0, r=300.0, b=400.0)
        self.numero_page = 1
        self.position: Position | None = None
        self.label = DocItemLabel.TEXT
        self.item = TextItem

    def avec_texte(self, texte: str):
        self.texte = texte
        return self

    def avec_bbox(self, bounding_box: BoundingBox):
        self.bounding_box = bounding_box
        return self

    def avec_numero_page(self, numero_page: int):
        self.numero_page = numero_page
        return self

    def a_la_position(self, position: Position):
        self.position = position
        return self

    def de_type_header(self):
        self.item = SectionHeaderItem
        self.label = DocItemLabel.SECTION_HEADER
        return self

    def de_type(self, label: DocItemLabel):
        if label == DocItemLabel.SECTION_HEADER:
            self.item = SectionHeaderItem
        if label == DocItemLabel.TABLE:
            self.item = TableItem
        self.label = label
        return self

    def construis(self) -> TextItem | TableItem:
        bounding_box = self.bounding_box
        if self.position:
            bounding_box = BoundingBox(
                l=self.position.x,
                t=self.position.y,
                r=self.position.largeur + self.position.x,
                b=self.position.hauteur + self.position.y,
            )
        if self.label == DocItemLabel.TABLE:
            return TableItem(
                data=TableData(
                    num_cols=1,
                    num_rows=1,
                    table_cells=[
                        TableCell(
                            text=self.texte,
                            start_row_offset_idx=0,
                            start_col_offset_idx=0,
                            end_row_offset_idx=1,
                            end_col_offset_idx=1,
                        )
                    ],
                ),
                label=self.label,
                self_ref="#/test/43",
                prov=[
                    ProvenanceItem(
                        page_no=self.numero_page,
                        bbox=bounding_box,
                        charspan=(0, len(self.texte)),
                    )
                ],
            )
        return self.item(
            text=self.texte,
            label=self.label,
            self_ref="#/test/42",
            orig="",
            prov=[
                ProvenanceItem(
                    page_no=self.numero_page,
                    bbox=bounding_box,
                    charspan=(0, len(self.texte)),
                )
            ],
        )


class ConstructeurDeSectionHeaderItem(ConstructeurDeTextItem):
    def avec_titre(self, titre: str):
        self.texte = titre
        return self

    def construis(self) -> SectionHeaderItem:
        return SectionHeaderItem(
            text=self.texte,
            label=DocItemLabel.SECTION_HEADER,
            self_ref="#/test/42",
            orig="",
            prov=[
                ProvenanceItem(
                    page_no=self.numero_page,
                    bbox=self.bounding_box,
                    charspan=(0, len(self.texte)),
                )
            ],
        )


@pytest.fixture
def un_convertisseur_avec_deux_bbox() -> Callable[[], Type[DocumentConverter]]:
    class ConverterDeTestAvecBbox(DocumentConverter):
        def convert(
            self,
            document: Union[Path, str, DocumentStream],  # TODO review naming
            headers: Optional[dict[str, str]] = None,
            raises_on_error: bool = True,
            max_num_pages: int = sys.maxsize,
            max_file_size: int = sys.maxsize,
            page_range: PageRange = (1, 1),
        ) -> ConversionResult:
            deuxieme_texte = (
                ConstructeurDeTextItem()
                .avec_texte("Texte seconde bbox")
                .avec_bbox(BoundingBox(l=200.0, t=200.0, r=300.0, b=190.0))
                .construis()
            )
            premier_texte = (
                ConstructeurDeTextItem()
                .avec_texte("Texte première bbox")
                .avec_bbox(BoundingBox(l=100.0, t=300.0, r=300.0, b=290.0))
                .construis()
            )
            return ConversionResult(
                document=DoclingDocument(
                    name="", texts=[deuxieme_texte, premier_texte]
                ),
                input=InputDocument(
                    format=InputFormat.PDF,
                    backend=PdfDocumentBackend,  # type: ignore[type-abstract]
                    path_or_stream=Path(),
                ),
            )

    def _convertisseur() -> Type[DocumentConverter]:
        return ConverterDeTestAvecBbox

    return _convertisseur


@pytest.fixture
def un_convertisseur_avec_deux_textes_dont_un_sans_bbox() -> Callable[
    [], Type[DocumentConverter]
]:
    class ConverterDeTestAvecBbox(DocumentConverter):
        def convert(
            self,
            document: Union[Path, str, DocumentStream],  # TODO review naming
            headers: Optional[dict[str, str]] = None,
            raises_on_error: bool = True,
            max_num_pages: int = sys.maxsize,
            max_file_size: int = sys.maxsize,
            page_range: PageRange = (1, 1),
        ) -> ConversionResult:
            deuxieme_texte = (
                ConstructeurDeTextItem()
                .avec_texte("Texte en seconde position")
                .construis()
            )
            premier_texte = (
                ConstructeurDeTextItem()
                .avec_texte("Texte première bbox")
                .avec_bbox(BoundingBox(l=100.0, t=300.0, r=300.0, b=290.0))
                .construis()
            )
            return ConversionResult(
                document=DoclingDocument(
                    name="", texts=[deuxieme_texte, premier_texte]
                ),
                input=InputDocument(
                    format=InputFormat.PDF,
                    backend=PdfDocumentBackend,  # type: ignore[type-abstract]
                    path_or_stream=Path(),
                ),
            )

    def _convertisseur() -> Type[DocumentConverter]:
        return ConverterDeTestAvecBbox

    return _convertisseur


@pytest.fixture
def un_convertisseur_avec_un_titre_et_un_texte() -> Callable[
    [], Type[DocumentConverter]
]:
    class ConverterDeTestAvecContenuSimple(DocumentConverter):
        def convert(
            self,
            document: Union[Path, str, DocumentStream],  # TODO review naming
            headers: Optional[dict[str, str]] = None,
            raises_on_error: bool = True,
            max_num_pages: int = sys.maxsize,
            max_file_size: int = sys.maxsize,
            page_range: PageRange = (1, 1),
        ) -> ConversionResult:
            premier_texte = (
                ConstructeurDeSectionHeaderItem()
                .avec_titre("Titre")
                .avec_bbox(BoundingBox(l=100.0, t=300.0, r=300.0, b=290.0))
                .construis()
            )
            deuxieme_texte = (
                ConstructeurDeTextItem()
                .avec_texte("Contenu du paragraphe.")
                .avec_bbox(BoundingBox(l=200.0, t=200.0, r=300.0, b=190.0))
                .construis()
            )
            return ConversionResult(
                document=DoclingDocument(
                    name="", texts=[deuxieme_texte, premier_texte]
                ),
                input=InputDocument(
                    format=InputFormat.PDF,
                    backend=PdfDocumentBackend,  # type: ignore[type-abstract]
                    path_or_stream=Path(),
                ),
            )

    def _convertisseur() -> Type[DocumentConverter]:
        return ConverterDeTestAvecContenuSimple

    return _convertisseur


@pytest.fixture
def un_constructeur_de_text_item() -> Callable[[], ConstructeurDeTextItem]:
    def _constructeur_de_doc_item() -> ConstructeurDeTextItem:
        return ConstructeurDeTextItem()

    return _constructeur_de_doc_item


class GenerateurDePagesStatique(GenerateurDePages):
    def __init__(self, numero_page: int = 0, contenu: str = "Un contenu"):
        super().__init__()
        self.numero_page = numero_page
        self.contenu = contenu

    def genere(self, elements_filtres: ElementsFiltres) -> dict[int, Page]:
        resultat: dict[int, Page] = {
            self.numero_page: PagePDF(
                self.numero_page,
                [BlocPagePDF(self.contenu, Position(x=0, y=0, hauteur=0, largeur=0))],
            ),
        }
        return resultat


class ChunkerDeTest(ChunkerDoclingMQC):
    def __init__(
        self,
        nom_fichier: str = "un_fichier_test.pdf",
        type_fichier: TypeFichier = TypeFichier.PDF,
        generateur: GenerateurDePagesStatique = GenerateurDePagesStatique(),
    ):
        super().__init__()
        self.nom_fichier = nom_fichier
        self.type_fichier = type_fichier
        self.generateur = generateur

    def applique(self, document_a_indexer: DocumentAIndexer) -> Document:
        document = Document(document_a_indexer.nom_document, document_a_indexer.url)
        document.genere_les_pages(self.generateur, [])
        return document


class ConstructeurDeChunker:
    def __init__(self):
        super().__init__()
        self.nom_fichier = "un_fichier_test.pdf"
        self.type_fichier = TypeFichier.PDF
        self.numero_page = 0
        self.contenu_page = "Un contenu"

    def avec_le_contenu(self, contenu: str):
        self.contenu_page = contenu
        return self

    def a_la_page(self, numero_page: int):
        self.numero_page = numero_page
        return self

    def avec_un_nom_de_fichier(self, nom_de_fichier: str):
        self.nom_fichier = nom_de_fichier
        return self

    def de_type_texte(self):
        self.type_fichier = TypeFichier.TEXTE
        return self

    def construis(self) -> ChunkerDeTest:
        generateur_de_pages_statique = GenerateurDePagesStatique(
            numero_page=self.numero_page, contenu=self.contenu_page
        )
        return ChunkerDeTest(
            nom_fichier=self.nom_fichier,
            type_fichier=self.type_fichier,
            generateur=generateur_de_pages_statique,
        )


@pytest.fixture
def un_chunker_avec_generation_de_page_statique() -> Callable[
    [], ConstructeurDeChunker
]:
    def _chunker_avec_generation_de_page_statique() -> ConstructeurDeChunker:
        return ConstructeurDeChunker()

    return _chunker_avec_generation_de_page_statique
