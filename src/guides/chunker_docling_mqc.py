import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import FormatOption, PdfFormatOption, DocumentConverter
from docling_core.transforms.chunker import BaseChunk, DocMeta

from guides.chunker_docling import ChunkerDocling
from guides.extrais_les_chunks import extrais_les_chunks
from guides.filtre_resultat import filtre_les_resultats
from guides.indexeur import DocumentPDF


@dataclass(frozen=True)
class BlocPage:
    numero_page: int
    texte: str
    ordre: tuple[float, float]


class ChunkerDoclingMQC(ChunkerDocling):
    def applique(self, document: DocumentPDF) -> list[BaseChunk]:
        nom_document_converti = Path(document.chemin_pdf)
        print(nom_document_converti)

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.generate_page_images = False
        pipeline_options.do_table_structure = False
        pipeline_options.images_scale = 3.0
        pipeline_options.generate_picture_images = False
        pipeline_options.ocr_options.force_full_page_ocr = False

        format_options: dict[InputFormat, FormatOption] = {
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
            )
        }

        converter = DocumentConverter(format_options=format_options)
        result = converter.convert(nom_document_converti)

        elements_filtres = filtre_les_resultats(result)

        return extrais_les_chunks(elements_filtres)

    @staticmethod
    def _est_entete(texte: str) -> bool:
        t = (texte or "").strip()
        if not t:
            return False
        if t.endswith((".", "…", "!", "?")):
            return False
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", t)
        if not (1 <= len(tokens) <= 6):
            return False
        if len(t) > 60:
            return False
        return True

    def blocs_par_page_avec_fusion(self, chunks) -> dict[int, list[BlocPage]]:
        par_page: dict[int, list[BlocPage]] = {}
        section_courante = ""

        for chunk in chunks:
            try:
                numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
                try:
                    meta = cast(DocMeta, chunk.meta)
                    bbox = meta.doc_items[0].prov[0].bbox
                    ordre = (-float(bbox.y1), float(bbox.x0))  # type:ignore  [attr-defined]
                except Exception:
                    ordre = (0.0, 0.0)

                texte = (chunk.text or "").strip()

                # Suivre la section courante
                if texte.startswith("[SECTION]"):
                    section_courante = texte
                elif (
                    texte.startswith("[TEXTE]")
                    and section_courante
                    and not any(
                        texte.startswith(prefix)
                        for prefix in ["[SOUS-TITRE]", "[NOTE]", "[SECTION]"]
                    )
                ):
                    # Ajouter le contexte de section au texte
                    texte = f"{section_courante}\n{texte}"

                bloc = BlocPage(numero_page=numero_page, texte=texte, ordre=ordre)
                par_page.setdefault(numero_page, []).append(bloc)
            except Exception as exc:
                logging.debug("Chunk ignoré: %s", exc)
                continue

        try:
            for page, blocs in par_page.items():
                blocs.sort(key=lambda b: b.ordre)
                fusionnes: list[BlocPage] = []
                i = 0
                while i < len(blocs):
                    courant = blocs[i]
                    if (
                        self._est_entete(courant.texte)
                        and i + 1 < len(blocs)
                        and not self._est_entete(blocs[i + 1].texte)
                    ):
                        suivant = blocs[i + 1]
                        texte_fusion = f"{courant.texte}\n{suivant.texte}"
                        fusionnes.append(
                            BlocPage(
                                numero_page=page,
                                texte=texte_fusion,
                                ordre=courant.ordre,
                            )
                        )
                        i += 2
                        continue
                    fusionnes.append(courant)
                    i += 1
                par_page[page] = fusionnes
        except Exception as exc:
            logging.warning("Erreur tri/fusion: %s", exc)

        return par_page
