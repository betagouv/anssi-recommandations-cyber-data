from abc import ABC, abstractmethod

from guides.indexeur import DocumentPDF
from docling_core.transforms.chunker import BaseChunk


class OptionsGuide(dict):
    structure_table: bool = True


OptionsGuides = dict[str, OptionsGuide]


class ChunkerDocling(ABC):
    @abstractmethod
    def applique(self, document: DocumentPDF) -> list[BaseChunk]:
        pass
