from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic

T_Bloc = TypeVar("T_Bloc", bound="BlocPage")


@dataclass(frozen=True)
class ContexteDuBloc:
    type_de_bloc: str | None = None
    code_recommandation: str | None = None
    titre: str | None = None
    section: str | None = None
    chemin_des_sections: tuple[str, ...] = ()
    niveau: int | None = None


@dataclass(frozen=True)
class BlocPage:
    texte: str
    numero_page: int | None
    position_page: int | None = None
    derniere_page: int | None = None
    pages: tuple[int, ...] = ()
    contexte: ContexteDuBloc | None = None


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
        pages: tuple[int, ...] = (),
        contexte: ContexteDuBloc | None = None,
    ) -> None:
        self.ajoute_bloc(
            classe_bloc(
                texte="\n".join(contenus),
                numero_page=numero_page,
                position_page=len(self.blocs),
                derniere_page=derniere_page,
                pages=pages,
                contexte=contexte,
            )
        )
