from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic

T_Bloc = TypeVar("T_Bloc", bound="BlocPage")


@dataclass(frozen=True)
class BlocPage:
    texte: str
    numero_page: int | None


@dataclass
class Page(ABC, Generic[T_Bloc]):
    numero_page: int | None
    blocs: list[T_Bloc] = field(default_factory=list)

    @abstractmethod
    def ajoute_bloc(self, bloc: T_Bloc) -> None:
        pass
