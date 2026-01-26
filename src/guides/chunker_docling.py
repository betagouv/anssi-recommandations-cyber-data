import json
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Type, cast

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, FormatOption, PdfFormatOption
from docling_core.transforms.chunker import BaseChunk, DocMeta

from guides.guide import Guide, Position
from guides.indexeur import DocumentPDF


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class TypeFichier(StrEnum):
    TEXTE = "TEXTE"
    PDF = "PDF"


class ChunkerDocling(ABC):
    def __init__(self, converter: Type[DocumentConverter] = DocumentConverter):
        super().__init__()
        fichier_options_path = Path(__file__).parent / "options_guides.json"
        with open(fichier_options_path, encoding="utf-8") as fichier_options_guides:
            self.options_guides: OptionsGuides = json.load(fichier_options_guides)  # type: ignore[annotation-unchecked]
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = True
        self.pipeline_options.generate_page_images = False
        self.pipeline_options.images_scale = 3.0
        self.pipeline_options.generate_picture_images = False
        self.pipeline_options.ocr_options.force_full_page_ocr = False
        self.nom_fichier = ""
        self.type_fichier = TypeFichier.PDF
        format_options: dict[InputFormat, FormatOption] = {
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=self.pipeline_options,
                backend=PyPdfiumDocumentBackend,
            )
        }
        self.converter = converter(format_options=format_options)

    def applique(self, document: DocumentPDF) -> Guide:
        clef: OptionsGuide | None = self.options_guides.get(
            Path(document.chemin_pdf).name
        )
        pdf_options = cast(
            PdfPipelineOptions,
            self.converter.format_to_options[InputFormat.PDF].pipeline_options,
        )
        if clef is not None and not clef["structure_table"]:
            print(f"Structure table - {clef['structure_table']}")
            pdf_options.do_table_structure = False
        else:
            pdf_options.do_table_structure = True
        result = self.converter.convert(Path(document.chemin_pdf))
        return self._cree_le_guide(result, document)

    @abstractmethod
    def _cree_le_guide(
        self, resultat_conversion: ConversionResult, document: DocumentPDF
    ) -> Guide:
        pass


def extrais_position(chunk: BaseChunk) -> Position:
    try:
        meta = cast(DocMeta, chunk.meta)
        bbox = meta.doc_items[0].prov[0].bbox
        return Position(
            x=float(bbox.l),
            y=float(bbox.t),
            largeur=float(bbox.r - bbox.l),
            hauteur=float(bbox.b - bbox.t),
        )
    except Exception:
        return Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0)
