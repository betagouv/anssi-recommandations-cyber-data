import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import NamedTuple, Optional

import jwt
from pydantic import BaseModel
from webauthn import (
    verify_authentication_response,
    base64url_to_bytes,
    generate_registration_options,
)
from webauthn.helpers import generate_challenge, bytes_to_base64url
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
    PublicKeyCredentialCreationOptions,
)

from configuration import Configuration, recupere_configuration, MQCData


class ReponseAccreditation(BaseModel):
    authenticatorData: str
    clientDataJSON: str
    signature: str
    userHandle: Optional[bytes] = None


class Accreditation(BaseModel):
    id: str
    rawId: str
    response: ReponseAccreditation
    type: str


class RequeteAccreditation(BaseModel):
    credential: Accreditation
    challenge: str


class ServiceAuthentification:
    def __init__(self, mqc_data: MQCData):
        super().__init__()
        self.mqc_data = mqc_data

    def initie_enrolement(self, utilisateur) -> PublicKeyCredentialCreationOptions:
        return generate_registration_options(
            rp_id=self.mqc_data.authentification.rp_id,
            rp_name="Tableau de bord admin MQC data",
            user_name=utilisateur,
            user_id=b"{utilisateur}",
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.EDDSA,
            ],
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED,
                require_resident_key=True,
            ),
        )

    def genere_challenge(self) -> str:
        return bytes_to_base64url(generate_challenge())

    def verifie_challenge(
        self, requete: Accreditation, challenge: str, clef_publique: str
    ):
        rp_id = self.mqc_data.authentification.rp_id
        credential = requete.model_dump_json()
        verify_authentication_response(
            credential=credential,
            expected_challenge=base64url_to_bytes(challenge),
            expected_rp_id=rp_id,
            expected_origin=self.mqc_data.authentification.origin,
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
            id=donnees_utilisateur["credential_id"],
            clef_publique=donnees_utilisateur["credential_public_key"],
        )

    def recupere_utilisateur_par_id_de_clef(
        self, id_clef: str
    ) -> UtilisateurEnCoursAuthentification | None:
        utilisateurs = self._recupere_utilisateurs()
        for donnees_utilisateur in utilisateurs.values():
            if donnees_utilisateur.get("credential_id") == id_clef:
                return UtilisateurEnCoursAuthentification(
                    id=donnees_utilisateur["credential_id"],
                    clef_publique=donnees_utilisateur["credential_public_key"],
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
