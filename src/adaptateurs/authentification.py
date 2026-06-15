from abc import ABC, abstractmethod
from typing import NamedTuple

from webauthn.helpers import generate_challenge


class ServiceAuthentification:
    def genere_challenge(self):
        return generate_challenge()


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


class EntrepotUtilisateursConcret(EntrepotUtilisateurs):
    def recupere_utilisateur_par_id_utilisateur(
        self, identifiant_utilisateur
    ) -> UtilisateurEnCoursAuthentification | None:
        return None


def fabrique_entrepot_utilisateurs() -> EntrepotUtilisateurs:
    return EntrepotUtilisateursConcret()
