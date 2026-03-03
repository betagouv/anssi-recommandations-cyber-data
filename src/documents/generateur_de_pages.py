from abc import ABC, abstractmethod
from typing import Callable

from documents.extrais_les_chunks import ElementsFiltres
from documents.page import BlocPagePDF, Page

type NumeroPage = int
type CreationDePage = Callable[[], Page]
type CreationDeBlocPage = Callable[[], BlocPagePDF]

type GenerationDePage = Callable[
    [], tuple[NumeroPage, CreationDePage, CreationDeBlocPage]
]


class GenerateurDePages(ABC):
    @abstractmethod
    def genere(self, elements_filtres: ElementsFiltres) -> dict[int, Page]:
        pass
