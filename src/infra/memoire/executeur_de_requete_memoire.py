from enum import StrEnum
from typing import Optional, Union, NamedTuple
from unittest.mock import Mock

from requests import Response

from adaptateurs.clients_albert import ReponseCollectionAlbert
from documents.indexeur.indexeur import (
    ReponseDocument,
    ReponseChunk,
    ReponseDocumentEnSucces,
    ReponseChunkEnSucces,
    ReponseDocumentEnErreur,
    ReponseChunkEnErreur,
)
from infra.executeur_requete import ExecuteurDeRequete


class ReponseTexteEnSucces(NamedTuple):
    texte: str


class ReponseTexteEnErreur(NamedTuple):
    pass


type ReponseTexte = Union[ReponseTexteEnSucces, ReponseTexteEnErreur]


class TypeRequete(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ReponseAttendueAbstraite:
    def __init__(
        self,
        reponse: ReponseDocument
        | ReponseChunk
        | ReponseCollectionAlbert
        | ReponseTexte,
    ):
        super().__init__()
        self.reponse_attendue = reponse


class ReponseAttendueOK(ReponseAttendueAbstraite):
    def __init__(
        self,
        reponse: ReponseDocumentEnSucces | ReponseChunkEnSucces | ReponseTexteEnSucces,
        type_requete: TypeRequete = TypeRequete.POST,
    ):
        super().__init__(reponse)
        self.type_requete = type_requete

    @property
    def status_code(self) -> int:
        return 201 if self.type_requete == TypeRequete.POST else 200

    @property
    def reponse(self) -> dict:
        return self.reponse_attendue._asdict()


class ReponseAttendueKO(ReponseAttendueAbstraite):
    def __init__(
        self,
        reponse: ReponseDocumentEnErreur | ReponseChunkEnErreur | ReponseTexteEnErreur,
        leve_une_erreur: str | None = None,
        type_requete: TypeRequete = TypeRequete.POST,
    ):
        super().__init__(reponse)
        self.leve_une_erreur = leve_une_erreur
        self.type_requete = type_requete

    @property
    def status_code(self) -> int:
        return 400 if self.type_requete == TypeRequete.POST else 404

    @property
    def reponse(self) -> dict:
        if self.leve_une_erreur is not None:
            raise RuntimeError(self.leve_une_erreur)
        return self.reponse_attendue._asdict()


class ReponseCreationCollectionOK(ReponseAttendueAbstraite):
    def __init__(self, reponse: ReponseCollectionAlbert):
        super().__init__(reponse)
        self.reponse_collection = reponse

    @property
    def status_code(self) -> int:
        return 201

    @property
    def reponse(self) -> dict:
        return self.reponse_collection._asdict()


class ReponseRecuperationCollectionOK(ReponseAttendueAbstraite):
    def __init__(self, reponse: ReponseCollectionAlbert):
        super().__init__(reponse)
        self.reponse_collection = reponse

    @property
    def status_code(self) -> int:
        return 200

    @property
    def reponse(self) -> dict:
        return self.reponse_collection._asdict()


class ReponseRecuperationCollectionKO(ReponseAttendueAbstraite):
    def __init__(self):
        super().__init__({"message": "La collection n’existe pas"})

    @property
    def status_code(self) -> int:
        return 404

    @property
    def reponse(self) -> dict:
        return {"message": "La collection n’existe pas"}


ReponseAttendue = Union[
    ReponseAttendueOK,
    ReponseAttendueKO,
    ReponseCreationCollectionOK,
    ReponseRecuperationCollectionOK,
    ReponseRecuperationCollectionKO,
]


class ExecuteurDeRequeteDeTest(ExecuteurDeRequete):
    def __init__(self, reponse_attendue: list[ReponseAttendue]):
        super().__init__()
        self.reponse_attendue = reponse_attendue
        self.payload_recu: dict[str, dict] = {}
        self.fichiers_recus: dict[str, dict] = {}
        self.index_courant = 0
        self.nombre_appels = 0
        self.url_appelee = ""

    def initialise_connexion_securisee(self, clef_api: str):
        pass

    def poste(self, url: str, payload: dict, fichiers: Optional[dict]) -> Response:
        self.nombre_appels += 1
        reponse = Mock()
        reponse_attendue = self.reponse_attendue[self.index_courant]
        reponse.status_code = reponse_attendue.status_code
        if (
            isinstance(reponse_attendue, ReponseAttendueKO)
            and reponse_attendue.leve_une_erreur is not None
        ):
            reponse.json.side_effect = RuntimeError(reponse_attendue.leve_une_erreur)
        else:
            reponse.json.return_value = reponse_attendue.reponse
        if fichiers is not None:
            self.fichiers_recus[url] = fichiers
        self.payload_recu[url] = payload
        self.index_courant += 1
        return reponse

    def recupere(self, url) -> Response:
        self.nombre_appels += 1
        self.url_appelee = url
        reponse = Mock()
        reponse_attendue = self.reponse_attendue[self.index_courant]
        self.index_courant += 1
        reponse.status_code = reponse_attendue.status_code
        if isinstance(reponse_attendue.reponse_attendue, ReponseTexteEnSucces):
            reponse.text = reponse_attendue.reponse_attendue.texte
        else:
            reponse.json.return_value = reponse_attendue.reponse
        return reponse
