import json
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Type, Literal, Callable

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    ApiVlmOptions,
    ResponseFormat,
    VlmPipelineOptions,
)
from pydantic import AnyUrl
from docling.document_converter import (
    DocumentConverter,
    FormatOption,
    PdfFormatOption,
    HTMLFormatOption,
)
from docling.pipeline.vlm_pipeline import VlmPipeline

from documents.docling.document import Document
from documents.indexeur.indexeur import DocumentAIndexer


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class TypeFichier(StrEnum):
    TEXTE = "TEXTE"
    PDF = "PDF"


def _initialise_options_pdf(
    cle_api: str = "",
    url_albert: str = "https://albert.api.etalab.gouv.fr/v1",
) -> tuple[InputFormat, PdfFormatOption]:
    vlm_options = ApiVlmOptions(
        url=AnyUrl(f"{url_albert.rstrip('/')}/chat/completions"),
        headers={"Authorization": f"Bearer {cle_api}"},
        params={"model": "mistralai/Mistral-Small-3.2-24B-Instruct-2506"},
        prompt=(
            "Convertis cette page de document en markdown. "
            "La page peut avoir une mise en page multi-colonnes : lis toujours de haut en bas, colonne gauche en premier, puis colonne droite. "
            "Chaque élément doit apparaître sous son titre de section correct — ne place jamais du contenu avant la section à laquelle il appartient. "
            "Règles de formatage :\n"
            "- Reproduis les caractères flèche exactement tels qu'ils apparaissent (→)\n"
            "- Indique le texte en gras avec **double astérisques**\n"
            "- Conserve les titres de section avec leur numérotation (ex. : '6.4 Établissement de clé')\n"
            "- Place chaque élément de liste sur sa propre ligne, précédé de →\n"
            "- Ajoute une ligne vide entre les sections\n"
            "- Pour les tableaux : extrais toujours TOUTES les colonnes et TOUTES les lignes complètement. "
            "Utilise le format markdown standard avec séparateur d'en-tête. "
            "Ne supprime jamais de colonnes même si elles semblent étroites dans l'original.\n"
            "- Les blocs de recommandation ont une mise en page caractéristique : un carré coloré à gauche contenant un code (R1, R18, R22…), "
            "une barre verticale de séparation, puis un titre en couleur à droite, suivi d'un texte de description en dessous. "
            "Ces quatre éléments forment UN SEUL bloc logique. "
            "Formate-les OBLIGATOIREMENT ainsi : '**R18 — Titre de la recommandation**' sur une ligne, "
            "puis le texte de description sur la ligne suivante. "
            "Le code Rxx et son titre ne doivent JAMAIS apparaître sur des lignes séparées ni le code Rxx être omis.\n"
            "- Les expressions mathématiques ou variables isolées (ex. : Pr, Pu, M, σ, g^r) ne doivent pas provoquer de saut de ligne. "
            "Réécris-les en notation LaTeX inline (ex. : $P_r$, $P_u$, $M$, $\\sigma$) et intègre-les dans le flux du texte sans interruption.\n"
            "- Retourne uniquement le contenu converti, sans commentaire."
        ),
        response_format=ResponseFormat.MARKDOWN,
        timeout=120,
    )
    pipeline_options = VlmPipelineOptions(
        vlm_options=vlm_options,
        enable_remote_services=True,
        generate_page_images=True,
        images_scale=3.0,
        generate_picture_images=False,
    )
    return InputFormat.PDF, PdfFormatOption(
        pipeline_cls=VlmPipeline,
        pipeline_options=pipeline_options,
        backend=PyPdfiumDocumentBackend,
    )


class ChunkerDocling(ABC):
    def __init__(
        self,
        converter: Type[DocumentConverter] = DocumentConverter,
        cle_api: str = "",
        url_albert: str = "https://albert.api.etalab.gouv.fr/v1",
    ):
        super().__init__()
        fichier_options_path = Path(__file__).parent / "../options_guides.json"
        with open(fichier_options_path, encoding="utf-8") as fichier_options_guides:
            self.options_guides: OptionsGuides = json.load(fichier_options_guides)  # type: ignore[annotation-unchecked]
        self.converter = converter()
        self.nom_fichier = ""
        self.type_fichier = TypeFichier.TEXTE
        self.cle_api = cle_api
        self.url_albert = url_albert

    @property
    def format_options(
        self,
    ) -> dict[
        Literal["PDF", "HTML"],
        Callable[[OptionsGuides | None], tuple[InputFormat, FormatOption]],
    ]:
        return {
            "PDF": lambda opts: _initialise_options_pdf(self.cle_api, self.url_albert),
            "HTML": lambda _option: (InputFormat.HTML, HTMLFormatOption()),
        }

    def applique(self, document: DocumentAIndexer) -> Document:
        clef: OptionsGuide | None = self.options_guides.get(Path(document.chemin).name)
        input_format, option_de_format = self.format_options[document.type](clef)
        self.converter.format_to_options[
            input_format
        ].pipeline_options = option_de_format.pipeline_options
        self.converter.format_to_options[
            input_format
        ].pipeline_cls = option_de_format.pipeline_cls
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
