import json
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Callable, Literal, Type, cast

from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter, FormatOption, HTMLFormatOption

from documents.docling.document import Document
from documents.indexeur.indexeur import DocumentAIndexer


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class TypeFichier(StrEnum):
    TEXTE = "TEXTE"
    PDF = "PDF"


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
            self.options_guides = cast(
                OptionsGuides,
                json.load(fichier_options_guides),
            )
        self.converter = converter()
        self.nom_fichier = ""
        self.type_fichier = TypeFichier.TEXTE
        self.cle_api = cle_api
        self.url_albert = url_albert

    @property
    def format_options(
        self,
    ) -> dict[
        Literal["HTML"],
        Callable[[OptionsGuides | None], tuple[InputFormat, FormatOption]],
    ]:
        return {"HTML": lambda _option: (InputFormat.HTML, HTMLFormatOption())}

    def applique(self, document: DocumentAIndexer) -> Document:
        if document.type == "PDF":
            raise RuntimeError("Le traitement PDF doit être fourni par le chunker PDF")
        clef: OptionsGuide | None = self.options_guides.get(Path(document.chemin).name)
        input_format, option_de_format = self.format_options["HTML"](clef)
        self.converter.format_to_options[
            input_format
        ].pipeline_options = option_de_format.pipeline_options
        self.converter.format_to_options[
            input_format
        ].pipeline_cls = option_de_format.pipeline_cls
        self.converter.format_to_options[
            input_format
        ].backend = option_de_format.backend
        resultat = self.converter.convert(document.chemin)
        return self._cree_le_document(resultat, document)

    @abstractmethod
    def _cree_le_document(
        self, resultat_conversion: ConversionResult, document: DocumentAIndexer
    ) -> Document:
        pass
