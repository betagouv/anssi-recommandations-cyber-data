from abc import ABC, abstractmethod
from typing import NamedTuple

from pydantic import BaseModel
from webauthn.helpers import generate_challenge


class ReponseAccreditation(BaseModel):
    authenticatorData: str
    clientDataJSON: str
    signature: str


class RequeteAccreditation(BaseModel):
    id: str
    rawId: str
    response: ReponseAccreditation
    type: str
    clientExtensionResults: dict


class ServiceAuthentification:
    def genere_challenge(self):
        return generate_challenge()

    def verifie_challenge(self, requete: RequeteAccreditation):
        pass


def fabrique_service_authentification() -> ServiceAuthentification:
    return ServiceAuthentification()


class UtilisateurEnCoursAuthentification(NamedTuple):
    id: str


class EntrepotUtilisateurs(ABC):
    @abstractmethod
    def recupere_utilisateur_par_id_utilisateur(
        self, identifiant_utilisateur
    ) -> UtilisateurEnCoursAuthentification | None:
        pass

    @abstractmethod
    def recupere_utilisateur_par_id_de_clef(
        self, id_clef: str
    ) -> UtilisateurEnCoursAuthentification | None:
        pass


class EntrepotUtilisateursConcret(EntrepotUtilisateurs):
    def recupere_utilisateur_par_id_utilisateur(
        self, identifiant_utilisateur
    ) -> UtilisateurEnCoursAuthentification | None:
        return None

    def recupere_utilisateur_par_id_de_clef(
        self, id_clef: str
    ) -> UtilisateurEnCoursAuthentification | None:
        return None


def fabrique_entrepot_utilisateurs() -> EntrepotUtilisateurs:
    return EntrepotUtilisateursConcret()


class ServiceGenerationToken:
    def genere_token(self) -> str:
        return ""


def fabrique_service_generation_token() -> ServiceGenerationToken:
    return ServiceGenerationToken()
