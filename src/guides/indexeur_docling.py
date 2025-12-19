import io
import json
from pathlib import Path
from typing import cast

import pikepdf
import requests
from docling.chunking import HierarchicalChunker, BaseChunk
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, FormatOption
from docling_core.transforms.chunker import DocMeta
from reportlab.pdfgen import canvas

from guides.indexeur import Indexeur, DocumentPDF, ReponseDocument


class ChunkerDocling:
    def applique(self, document: DocumentPDF) -> list[BaseChunk]:
        nom_document_converti = Path(document.chemin_pdf).name.replace(
            ".pdf", "_converti.pdf"
        )
        with pikepdf.open(document.chemin_pdf) as pdf:
            pdf.save(nom_document_converti)
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.generate_page_images = False

        format_options: dict[InputFormat, FormatOption] = {
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }

        converter = DocumentConverter(format_options=format_options)
        result = converter.convert(nom_document_converti)

        chunker = HierarchicalChunker()
        return list(chunker.chunk(result.document))


class IndexeurDocling(Indexeur):
    def __init__(self, url: str, chunker: ChunkerDocling = ChunkerDocling()):
        super().__init__()
        self.chunker = chunker
        self.url = url
        self.session = requests.Session()

    def ajoute_documents(
        self, documents: list[DocumentPDF], id_collection: str | None
    ) -> list[ReponseDocument]:
        reponse_documents = []
        for document in documents:
            reponse_documents.extend(self.__ajoute_document(document, id_collection))

        return reponse_documents

    def __ajoute_document(
        self, document: DocumentPDF, id_collection: str | None
    ) -> list[ReponseDocument]:
        reponses = []
        chunks = list(self.chunker.applique(document))

        def bufferise() -> io.BytesIO:
            le_buffer = io.BytesIO()
            pdf = canvas.Canvas(le_buffer)
            pdf.drawString(50, 750, contenu_paragraphe_txt)
            pdf.showPage()
            pdf.save()

            le_buffer.seek(0)
            return le_buffer

        for index, chunk in enumerate(chunks, start=1):
            contenu_paragraphe_txt = chunk.text
            if len(contenu_paragraphe_txt) > 1:
                numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                fichiers = {
                    "file": (
                        Path(document.chemin_pdf).name,
                        (bufferise()),
                        "application/pdf",
                    )
                }
                payload = {
                    "collection": str(id_collection),
                    "metadata": json.dumps(
                        {"source_url": document.url_pdf, "page": numero_page}
                    ),
                    "chunker": "NoSplitter",
                }
                response = self.session.post(
                    f"{self.url}/documents", data=payload, files=fichiers
                )
                result = response.json()
                reponses.append(
                    ReponseDocument(
                        id=result["id"],
                        name=result.get("name", Path(document.chemin_pdf).name),
                        collection_id=result.get("collection_id", str(id_collection)),
                        created_at=result.get("created_at", ""),
                        updated_at=result.get("updated_at", ""),
                    )
                )
        return reponses
