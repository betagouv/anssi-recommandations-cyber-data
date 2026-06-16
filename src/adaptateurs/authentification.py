import json
from abc import ABC, abstractmethod
from typing import NamedTuple

from pydantic import BaseModel
from webauthn.helpers import generate_challenge

from configuration import Configuration, recupere_configuration


class ReponseAccreditation(BaseModel):
    authenticatorData: str
    clientDataJSON: str
    signature: str


class Accreditation(BaseModel):
    id: str
    rawId: str
    response: ReponseAccreditation
    type: str
    clientExtensionResults: dict


class RequeteAccreditation(BaseModel):
    credential: Accreditation
    challenge: str


class ServiceAuthentification:
    def genere_challenge(self):
        return generate_challenge()

    def verifie_challenge(self, requete: Accreditation, challenge: str, clef_publique):
        pass


def fabrique_service_authentification() -> ServiceAuthentification:
    return ServiceAuthentification()


class UtilisateurEnCoursAuthentification(NamedTuple):
    id: str
    clef_publique: str


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
    def __init__(self, utilisateurs_mqc: str):
        self.utilisateurs_mqc = utilisateurs_mqc

    def _recupere_utilisateurs(self) -> dict:
        try:
            return json.loads(self.utilisateurs_mqc)
        except json.JSONDecodeError:
            return {}

    def recupere_utilisateur_par_id_utilisateur(
        self, identifiant_utilisateur
    ) -> UtilisateurEnCoursAuthentification | None:
        utilisateurs = self._recupere_utilisateurs()
        donnees_utilisateur = utilisateurs.get(identifiant_utilisateur)
        if not donnees_utilisateur:
            return None
        return UtilisateurEnCoursAuthentification(
            id=donnees_utilisateur["id"],
            clef_publique=donnees_utilisateur["response"]["clef_publique"],
        )

    def recupere_utilisateur_par_id_de_clef(
        self, id_clef: str
    ) -> UtilisateurEnCoursAuthentification | None:
        utilisateurs = self._recupere_utilisateurs()
        for donnees_utilisateur in utilisateurs.values():
            if donnees_utilisateur.get("id") == id_clef:
                return UtilisateurEnCoursAuthentification(
                    id=donnees_utilisateur["id"],
                    clef_publique=donnees_utilisateur["response"]["clef_publique"],
                )
        return None


def fabrique_entrepot_utilisateurs() -> EntrepotUtilisateurs:
    la_configuration: Configuration = recupere_configuration()
    return EntrepotUtilisateursConcret(la_configuration.utilisateurs_mqc)


class ServiceGenerationToken:
    def genere_token(self) -> str:
        return ""


def fabrique_service_generation_token() -> ServiceGenerationToken:
    return ServiceGenerationToken()
