import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type, cast

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter, FormatOption, PdfFormatOption
from docling_core.transforms.chunker import BaseChunk, DocMeta

from guides.guide import Guide, Position
from guides.indexeur import DocumentPDF


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class ChunkerDocling(ABC):
    def __init__(self):
        super().__init__()
        with open("src/guides/options_guides.json") as fichier_options_guides:
            self.options_guides: OptionsGuides = json.load(fichier_options_guides)  # type: ignore[annotation-unchecked]
        self.pipeline_options = PdfPipelineOptions()
        self.pipeline_options.do_ocr = True
        self.pipeline_options.generate_page_images = False
        self.pipeline_options.images_scale = 3.0
        self.pipeline_options.generate_picture_images = False
        self.pipeline_options.ocr_options.force_full_page_ocr = False

    def applique(
        self,
        document: DocumentPDF,
        converter: Type[DocumentConverter] = DocumentConverter,
    ) -> Guide:
        clef: OptionsGuide | None = self.options_guides.get(
            Path(document.chemin_pdf).name
        )
        if clef is not None and not clef["structure_table"]:
            print(f"Structure table - {clef['structure_table']}")
            self.pipeline_options.do_table_structure = False
        format_options: dict[InputFormat, FormatOption] = {
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=self.pipeline_options,
                backend=PyPdfiumDocumentBackend,
            )
        }
        result = converter(format_options=format_options).convert(
            Path(document.chemin_pdf)
        )
        return self._cree_le_guide(result)

    @abstractmethod
    def _cree_le_guide(self, document: ConversionResult) -> Guide:
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
