from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic

T_Bloc = TypeVar("T_Bloc", bound="BlocPage")


@dataclass(frozen=True)
class BlocPage:
    texte: str
    numero_page: int | None
    position_page: int | None = None
    derniere_page: int | None = None


@dataclass
class Page(ABC, Generic[T_Bloc]):
    numero_page: int | None
    blocs: list[T_Bloc] = field(default_factory=list)

    @abstractmethod
    def ajoute_bloc(self, bloc: T_Bloc) -> None:
        pass

    def ajoute_blocs(
        self,
        contenus: list[str],
        numero_page: int,
        classe_bloc: type[T_Bloc],
        derniere_page: int | None = None,
    ) -> None:
        position_page = len(self.blocs)
        self.ajoute_bloc(
            classe_bloc(
                texte="\n".join(contenus),
                numero_page=numero_page,
                position_page=position_page,
                derniere_page=derniere_page,
            )
        )
