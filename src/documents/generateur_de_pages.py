from abc import ABC, abstractmethod
from typing import Callable

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
    def genere(self, elements_filtres: ElementsFiltres) -> dict[int, Page]:
        pass
