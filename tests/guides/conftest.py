import sys
from pathlib import Path
from typing import Callable, Type, Union, Optional
from unittest.mock import Mock

import pytest
from docling.backend.pdf_backend import PdfDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling.document_converter import ConversionResult
from docling.datamodel.settings import PageRange
from docling.document_converter import DocumentConverter
from docling_core.types import DoclingDocument
from docling_core.types.doc import BoundingBox, ProvenanceItem, TextItem, DocItemLabel
from docling_core.types.io import DocumentStream
from requests import Session

from guides.indexeur import (
    ReponseDocument,
    ReponseDocumentEnSucces,
)


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
def mock_post_session_creation_document() -> Callable[[Session, ReponseDocument], None]:
    def _mock(session: Session, reponse_attendue: ReponseDocument) -> None:
        mock_response = Mock()
        mock_response.json.return_value = reponse_attendue._asdict()
        session.post = Mock(return_value=mock_response)  # type: ignore[method-assign]

    return _mock


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

    def avec_texte(self, texte: str):
        self.texte = texte
        return self

    def avec_bbox(self, bounding_box: BoundingBox):
        self.bounding_box = bounding_box
        return self

    def avec_numero_page(self, numero_page: int):
        self.numero_page = numero_page
        return self

    def construis(self) -> TextItem:
        return TextItem(
            text=self.texte,
            label=DocItemLabel.TEXT,
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
def un_convertisseur_se_basant_sur_un_guide_anssi() -> Callable[
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
            numero_page = 11
            premier_paragraphe = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte(
                    "afin d’accélérer leur recherche, puis de comparer "
                    "automatiquement chacune d’entre elles à une empreinte "
                    "volée jusqu’à trouver une égalité qui prouvera que le "
                    "mot de passe recherché a été trouvé."
                )
                .avec_bbox(BoundingBox(l=86.0, t=767.0, r=536.0, b=797.0))
                .construis()
            )
            deuxieme_paragraphe = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte(
                    "Attaque par ingénierie sociale. Cette "
                    "attaque consiste à récupérer un mot "
                    "de passe par des moyens détournés "
                    "comme l’hameçonnage ou bien l’usurpation "
                    "d’identité."
                )
                .avec_bbox(BoundingBox(l=73.0, t=716.0, r=536.0, b=740.0))
                .construis()
            )
            premiere_entete = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("Menace")
                .avec_bbox(BoundingBox(l=78.0, t=620.0, r=117.0, b=627.0))
                .construis()
            )
            premiere_ligne_colonne_1 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("Recherche exhaustive")
                .avec_bbox(BoundingBox(l=78.0, t=580.0, r=181.0, b=588.0))
                .construis()
            )
            deuxieme_ligne_colonne_1 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("Recherche par dictionnaire")
                .avec_bbox(BoundingBox(l=78.0, t=536.0, r=207.0, b=546.0))
                .construis()
            )
            deuxieme_entete = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("Contre-mesures")
                .avec_bbox(BoundingBox(l=317.0, t=620.0, r=395.0, b=627.0))
                .construis()
            )
            premiere_ligne_colonne_2 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("Limite temporelle entre chaque essai (contre les")
                .avec_bbox(BoundingBox(l=317.0, t=601.0, r=543.0, b=611.0))
                .construis()
            )
            deuxieme_ligne_colonne_2 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("attaquants en ligne) et fonctions de hachage ité-")
                .avec_bbox(BoundingBox(l=317.0, t=587.0, r=543.0, b=597.0))
                .construis()
            )
            troisieme_ligne_colonne_2 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("ratives dédiées (contre les attaquants en ligne et")
                .avec_bbox(BoundingBox(l=317.0, t=573.0, r=543.0, b=583.0))
                .construis()
            )
            quatrieme_ligne_colonne_2 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("hors ligne)")
                .avec_bbox(BoundingBox(l=317.0, t=558.0, r=367.0, b=568.0))
                .construis()
            )
            cinquieme_ligne_colonne_2 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("Mots de passe robustes et aléatoires et coffre-")
                .avec_bbox(BoundingBox(l=317.0, t=544.0, r=543.0, b=554.0))
                .construis()
            )
            sixieme_ligne_colonne_2 = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte("fort de mots de passe")
                .avec_bbox(BoundingBox(l=317.0, t=529.0, r=417.0, b=539.0))
                .construis()
            )
            legende_tableau = (
                ConstructeurDeTextItem()
                .avec_numero_page(numero_page)
                .avec_texte(
                    "TABLE 1 – Récapitulatif des menaces et contre-mesures sur les mots de passe"
                )
                .avec_bbox(BoundingBox(l=123.0, t=476.0, r=484.0, b=486.0))
                .construis()
            )

            return ConversionResult(
                document=DoclingDocument(
                    name="",
                    texts=[
                        deuxieme_paragraphe,
                        premiere_ligne_colonne_1,
                        deuxieme_ligne_colonne_2,
                        premiere_ligne_colonne_2,
                        premier_paragraphe,
                        troisieme_ligne_colonne_2,
                        deuxieme_ligne_colonne_1,
                        quatrieme_ligne_colonne_2,
                        deuxieme_entete,
                        cinquieme_ligne_colonne_2,
                        premiere_entete,
                        sixieme_ligne_colonne_2,
                        legende_tableau,
                    ],
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
def un_convertisseur_toto() -> Callable[[], Type[DocumentConverter]]:
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
                ConstructeurDeTextItem()
                .avec_texte("Titre")
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
