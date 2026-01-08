import json
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import FormatOption, PdfFormatOption, DocumentConverter
from docling_core.transforms.chunker import BaseChunk, HierarchicalChunker

from guides.indexeur import DocumentPDF
from guides.chunker_docling import OptionsGuide, OptionsGuides, ChunkerDocling


class ChunkerDoclingHierarchique(ChunkerDocling):
    def __init__(self):
        super().__init__()
        with open("src/guides/options_guides.json") as fichier_options_guides:
            self.options_guides: OptionsGuides = json.load(fichier_options_guides)  # type: ignore[annotation-unchecked]

    def applique(self, document: DocumentPDF) -> list[BaseChunk]:
        nom_document_converti = Path("donnees/conversion") / Path(
            document.chemin_pdf
        ).name.replace(".pdf", "_converti.pdf")
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        clef: OptionsGuide | None = self.options_guides.get(
            Path(document.chemin_pdf).name
        )
        if clef is not None and not clef["structure_table"]:
            print(f"Structure table - {clef['structure_table']}")
            pipeline_options.do_table_structure = False
        pipeline_options.generate_page_images = False

        format_options: dict[InputFormat, FormatOption] = {
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }

        converter = DocumentConverter(format_options=format_options)
        result = converter.convert(nom_document_converti)

        chunker = HierarchicalChunker()
        chunks = []

        def est_lisible(text: str) -> bool:
            if not text:
                return False

            alpha = sum(c.isalpha() for c in text)
            ratio = alpha / max(len(text), 1)

            return ratio > 0.5 and " " in text

        for chunk in chunker.chunk(result.document):
            if est_lisible(chunk.text):
                chunks.append(chunk)
        return chunks
