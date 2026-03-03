import json
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Type, Literal, Callable

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    FormatOption,
    PdfFormatOption,
    HTMLFormatOption,
)

from documents.document import Document
from documents.indexeur import DocumentAIndexer


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class TypeFichier(StrEnum):
    TEXTE = "TEXTE"
    PDF = "PDF"


def __initialise_options_pdf(
    options_guides: OptionsGuides | None,
) -> tuple[InputFormat, PdfFormatOption]:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.generate_page_images = False
    pipeline_options.images_scale = 3.0
    pipeline_options.generate_picture_images = False
    pipeline_options.ocr_options.force_full_page_ocr = False
    if options_guides is not None and not options_guides.get("structure_table", True):
        pipeline_options.do_table_structure = False
    else:
        pipeline_options.do_table_structure = True
    return InputFormat.PDF, PdfFormatOption(
        pipeline_options=pipeline_options,
        backend=PyPdfiumDocumentBackend,
    )


format_options: dict[
    Literal["PDF", "HTML"],
    Callable[[OptionsGuides | None], tuple[InputFormat, FormatOption]],
] = {
    "PDF": __initialise_options_pdf,
    "HTML": lambda _option: (InputFormat.HTML, HTMLFormatOption()),
}


class ChunkerDocling(ABC):
    def __init__(self, converter: Type[DocumentConverter] = DocumentConverter):
        super().__init__()
        fichier_options_path = Path(__file__).parent / "options_guides.json"
        with open(fichier_options_path, encoding="utf-8") as fichier_options_guides:
            self.options_guides: OptionsGuides = json.load(fichier_options_guides)  # type: ignore[annotation-unchecked]
        self.converter = converter()
        self.nom_fichier = ""
        self.type_fichier = TypeFichier.TEXTE

    def applique(self, document: DocumentAIndexer) -> Document:
        clef: OptionsGuide | None = self.options_guides.get(Path(document.chemin).name)
        input_format, option_de_format = format_options[document.type](clef)
        self.converter.format_to_options[
            input_format
        ].pipeline_options = option_de_format.pipeline_options
        self.converter.format_to_options[
            input_format
        ].backend = option_de_format.backend
        result = self.converter.convert(document.chemin)
        return self._cree_le_document(result, document)

    @abstractmethod
    def _cree_le_document(
        self, resultat_conversion: ConversionResult, document: DocumentAIndexer
    ) -> Document:
        pass
