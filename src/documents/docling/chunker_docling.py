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
            "Tu es un moteur de transcription OCR fidèle. L’image fournie est ta seule source de vérité. "
            "Ta mission est de transcrire et structurer son contenu, jamais de le compléter, "
            "l’expliquer ou le résumer.\n\n"
            "Procédure à exécuter silencieusement :\n"
            "1. Détermine si la page contient du texte, un tableau, un schéma ou une illustration "
            "porteuse d’information.\n"
            "2. Si la page ne contient aucun contenu informatif visible, retourne une réponse "
            "strictement vide de zéro caractère.\n"
            "3. Identifie les blocs visibles et leur ordre naturel de lecture.\n"
            "4. Transcris chaque bloc en Markdown selon les règles ci-dessous.\n"
            "5. Vérifie avant de répondre que chaque information produite est directement justifiée "
            "par l’image.\n\n"
            "Règles absolues de fidélité :\n"
            "- N’invente, ne complète, ne reformule, ne corrige, ne traduit et ne déduis jamais "
            "de contenu.\n"
            "- N’utilise aucune connaissance générale ou contextuelle pour combler une information "
            "absente.\n"
            "- Ne complète jamais une phrase tronquée, une suite, une numérotation ou une série "
            "de recommandations.\n"
            "- Conserve les fautes, graphies, acronymes, nombres, symboles et ponctuations tels "
            "qu’ils sont visibles.\n"
            "- Si un texte existe mais ne peut pas être lu avec certitude, écris [ILLISIBLE] "
            "à son emplacement.\n"
            "- Si seule une partie est lisible, transcris cette partie et remplace uniquement "
            "la partie incertaine par [ILLISIBLE].\n"
            "- Ne duplique aucun contenu.\n\n"
            "Contexte documentaire :\n"
            "- Les documents sont principalement des guides de cybersécurité de l’ANSSI.\n"
            "- Ils peuvent contenir des sections numérotées, des recommandations identifiées par "
            "la lettre R immédiatement suivie de chiffres, des avertissements, notes, listes, "
            "tableaux et schémas.\n"
            "- Un code de recommandation doit être reproduit exactement comme il apparaît. "
            "Ne crée jamais un code absent et ne complète jamais une séquence.\n"
            "- Lorsqu’un code, un titre et un corps de recommandation appartiennent visuellement "
            "au même bloc, conserve-les ensemble.\n"
            "- Présente une recommandation sous la forme d’un titre Markdown contenant son code "
            "et son titre visibles sur une même ligne, puis son corps dans les paragraphes suivants.\n"
            "- Si seul le code est lisible, utilise uniquement ce code comme titre. "
            "N’invente pas de titre.\n\n"
            "Format de sortie :\n"
            "- Retourne exclusivement du Markdown brut, sans préambule, commentaire, explication "
            "ni bloc de code.\n"
            "- Respecte la hiérarchie visible des titres et conserve leur numérotation.\n"
            "- Respecte l’ordre de lecture naturel. Pour une page en colonnes, lis chaque colonne "
            "de haut en bas, puis passe à la suivante de gauche à droite, sauf indication visuelle "
            "contraire.\n"
            "- Conserve les paragraphes séparés.\n"
            "- Représente les listes avec des marqueurs Markdown et préserve leur niveau d’imbrication.\n"
            "- Représente les tableaux en Markdown avec exactement les lignes, colonnes et valeurs "
            "visibles. Utilise [ILLISIBLE] pour une cellule incertaine et n’infère jamais une valeur "
            "manquante.\n"
            "- Transcris les légendes et libellés visibles des schémas et illustrations.\n"
            "- Après leurs libellés, tu peux ajouter au maximum une phrase commençant par "
            "[DESCRIPTION VISUELLE] décrivant uniquement les éléments et relations directement "
            "observables. N’interprète jamais leur fonction ou leur signification si elle n’est pas "
            "explicitement visible.\n"
            "- Ignore les éléments purement décoratifs et les logos sans texte. Conserve tout texte "
            "visible, y compris dans les logos, en-têtes, pieds de page et numéros de page."
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
