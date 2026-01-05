import json
import logging
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import cast, Generator

from docling.chunking import HierarchicalChunker, BaseChunk
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, FormatOption
from docling_core.transforms.chunker import DocMeta

from guides.executeur_requete import ExecuteurDeRequete
from guides.indexeur import (
    Indexeur,
    DocumentPDF,
    ReponseDocument,
    ReponseDocumentEnSucces,
    ReponseDocumentEnErreur,
)
from guides.multi_processeur import Multiprocesseur

for name in (
    "docling",
    "docling.pipeline",
    "docling.document_converter",
    "docling.chunking",
):
    logging.getLogger(name).setLevel(logging.CRITICAL)


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class ChunkerDocling:
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


@dataclass
class DocumentsAAjouter:
    documents: list[DocumentPDF]
    id_collection: str | None = None
    numero_liste_en_cours: int = 0


class IndexeurDocling(Indexeur):
    def __init__(
        self,
        url: str,
        clef_api: str,
        chunker: ChunkerDocling = ChunkerDocling(),
        executeur_de_requete: ExecuteurDeRequete = ExecuteurDeRequete(),
        multi_processeur: Multiprocesseur = Multiprocesseur(),
    ):
        super().__init__()
        self.multi_processeur = multi_processeur
        self.executeur_de_requete = executeur_de_requete
        self.chunker = chunker
        self.url = url
        self.clef_api = clef_api

    def ajoute_documents(
        self, documents: list[DocumentPDF], id_collection: str | None
    ) -> list[ReponseDocument]:
        reponse_documents = []

        def decoupe_la_liste_de_documents(
            iterable: list[DocumentPDF],
        ) -> Generator[DocumentsAAjouter]:
            it = iter(iterable)
            i = 0
            while True:
                sous_ensemble = list(islice(it, 15))
                if not sous_ensemble:
                    break
                yield DocumentsAAjouter(
                    documents=sous_ensemble,
                    id_collection=id_collection,
                    numero_liste_en_cours=i,
                )
                i = i + 1

        documents_crees: list[list[ReponseDocument]] = self.multi_processeur.execute(
            self._ajoute_les_documents, decoupe_la_liste_de_documents(documents)
        )
        reponse_documents.extend(
            [x for sous_liste in documents_crees for x in sous_liste]
        )
        return reponse_documents

    def _ajoute_les_documents(
        self, documents: DocumentsAAjouter
    ) -> list[ReponseDocument]:
        reponse_documents = []
        for indice, document in enumerate(documents.documents):
            print(
                f"[Liste {documents.numero_liste_en_cours}][{indice + 1} de {len(documents.documents)}] - Découpage du document {document.url_pdf}"
            )
            reponse_documents.extend(
                self.__ajoute_document(document, documents.id_collection)
            )
            if indice + 1 == len(documents.documents):
                print(f"[Liste {documents.numero_liste_en_cours}] - FINI")
        return reponse_documents

    def __ajoute_document(
        self, document: DocumentPDF, id_collection: str | None
    ) -> list[ReponseDocument]:
        nom_du_document = Path(document.chemin_pdf).name
        reponses: list[ReponseDocument] = []
        try:
            chunks = list(self.chunker.applique(document))

            def bufferise() -> bytes:
                from reportlab.pdfgen import canvas
                import io

                le_buffer = io.BytesIO()
                pdf = canvas.Canvas(le_buffer)
                pdf.drawString(50, 750, contenu_paragraphe_txt)
                pdf.showPage()
                pdf.save()

                le_buffer.seek(0)
                return le_buffer.getvalue()

            self.executeur_de_requete.initialise(self.clef_api)

            for index, chunk in enumerate(chunks, start=1):
                contenu_paragraphe_txt = chunk.text
                if len(contenu_paragraphe_txt) > 1:
                    buffer_pdf = bufferise()
                    numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                    fichiers = {
                        "file": (
                            nom_du_document,
                            (buffer_pdf),
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
                    response = self.executeur_de_requete.poste(
                        f"{self.url}/documents", payload, fichiers
                    )
                    result = response.json()
                    if response.status_code != 201:
                        reponses.append(
                            ReponseDocumentEnErreur(
                                detail=result.get("detail", "Une erreur est survenue"),
                                document_en_erreur=nom_du_document,
                            )
                        )
                    else:
                        reponses.append(
                            ReponseDocumentEnSucces(
                                id=result["id"],
                                name=result.get("name", nom_du_document),
                                collection_id=result.get(
                                    "collection_id", str(id_collection)
                                ),
                                created_at=result.get("created_at", ""),
                                updated_at=result.get("updated_at", ""),
                            )
                        )
        except Exception as e:
            reponses.append(
                ReponseDocumentEnErreur(
                    detail=str(e), document_en_erreur=nom_du_document
                )
            )
        return reponses
