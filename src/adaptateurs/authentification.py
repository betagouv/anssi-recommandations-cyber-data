import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import NamedTuple

import jwt
from pydantic import BaseModel
from webauthn import verify_authentication_response, base64url_to_bytes
from webauthn.helpers import generate_challenge, bytes_to_base64url

from configuration import Configuration, recupere_configuration, MQCData


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
    def __init__(self, mqc_data: MQCData):
        super().__init__()
        self.mqc_data = mqc_data

    def genere_challenge(self) -> str:
        return bytes_to_base64url(generate_challenge())

    def verifie_challenge(
        self, requete: Accreditation, challenge: str, clef_publique: str
    ):
        verify_authentication_response(
            credential=requete.model_dump_json(),
            expected_challenge=base64url_to_bytes(challenge),
            expected_rp_id=self.mqc_data.hote,
            expected_origin=self.mqc_data.url_hote,
            credential_public_key=base64url_to_bytes(clef_publique),
            credential_current_sign_count=0,
        )


def fabrique_service_authentification() -> ServiceAuthentification:
    la_configuration = recupere_configuration()
    return ServiceAuthentification(la_configuration.mqc_data)


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
            clef_publique=donnees_utilisateur["response"]["publicKey"],
        )

    def recupere_utilisateur_par_id_de_clef(
        self, id_clef: str
    ) -> UtilisateurEnCoursAuthentification | None:
        utilisateurs = self._recupere_utilisateurs()
        for donnees_utilisateur in utilisateurs.values():
            if donnees_utilisateur.get("id") == id_clef:
                return UtilisateurEnCoursAuthentification(
                    id=donnees_utilisateur["id"],
                    clef_publique=donnees_utilisateur["response"]["publicKey"],
                )
        return None


def fabrique_entrepot_utilisateurs() -> EntrepotUtilisateurs:
    la_configuration: Configuration = recupere_configuration()
    return EntrepotUtilisateursConcret(la_configuration.utilisateurs_mqc)


class ServiceGenerationToken:
    def __init__(self, secret_jwt: str):
        super().__init__()
        self.secret_jwt = secret_jwt

    def genere_token(self) -> str:
        payload = {
            "name": "Token Admin MQC Data",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=2),
        }

        token = jwt.encode(
            payload,
            self.secret_jwt,
            algorithm="HS256",
        )
        return token


def fabrique_service_generation_token() -> ServiceGenerationToken:
    la_configuration = recupere_configuration()
    return ServiceGenerationToken(la_configuration.secret_jwt)
