from abc import ABC, abstractmethod
from typing import Callable

from docling_core.transforms.chunker import BaseChunk

from documents.page import BlocPagePDF, Page

type NumeroPage = int
type CreationDePage = Callable[[], Page]
type CreationDeBlocPage = Callable[[], BlocPagePDF]

type GenerationDePage = Callable[
    [], tuple[NumeroPage, CreationDePage, CreationDeBlocPage]
]


class GenerateurDePages(ABC):
    @abstractmethod
    def genere(self, chunks: list[BaseChunk]) -> dict[int, Page]:
        pass
