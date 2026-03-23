from abc import ABC, abstractmethod
from typing import Callable, Optional

from docling_core.types import DoclingDocument

from documents.elements_filtres import ElementsFiltres
from documents.page import Page, BlocPage

type NumeroPage = int
type CreationDePage = Callable[[], Page]
type CreationDeBlocPage = Callable[[], BlocPage]

type GenerationDePage = Callable[
    [], tuple[NumeroPage, CreationDePage, CreationDeBlocPage]
]


class GenerateurDePages(ABC):
    @abstractmethod
    def genere(
        self, elements_filtres: ElementsFiltres, document: Optional[DoclingDocument]
    ) -> dict[int, Page]:
        pass
