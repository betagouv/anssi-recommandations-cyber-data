from typing import Any

from fastapi import APIRouter, Response
from fastapi.params import Depends
from pydantic import BaseModel
from webauthn import base64url_to_bytes, options_to_json, verify_registration_response
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticatorAttestationResponse,
)

from adaptateurs.authentification import (
    fabrique_service_authentification,
    ServiceAuthentification,
    EntrepotUtilisateurs,
    fabrique_entrepot_utilisateurs,
    RequeteAccreditation,
    fabrique_service_generation_token,
    ServiceGenerationToken,
)
from infra.logger import log
import base64

auth = APIRouter(prefix="/auth")


class RequeteAuthentification(BaseModel):
    utilisateur: str


class RequeteVerificationEnrolement(BaseModel):
    credential: dict[str, Any]
    challenge: str


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def verified_registration_to_dict(vr):
    return {
        "credential_id": b64u(vr.credential_id),
        "credential_public_key": b64u(vr.credential_public_key),
        "sign_count": vr.sign_count,
    }


class RequeteEnrolement(BaseModel):
    utilisateur: str


@auth.post("/enrole")
def enrole(
    requete: RequeteEnrolement,
    service_generation_de_challenge: ServiceAuthentification = Depends(  # type: ignore[assignment]
        fabrique_service_authentification
    ),
):
    options = service_generation_de_challenge.initie_enrolement(requete.utilisateur)
    return {
        "options": options_to_json(options),
        "challenge": bytes_to_base64url(options.challenge),
    }


@auth.post("/verifie-enrolement")
def verifie_enrolement(requete: RequeteVerificationEnrolement):
    credential = RegistrationCredential(
        id=requete.credential["id"],
        raw_id=base64url_to_bytes(requete.credential["rawId"]),
        response=AuthenticatorAttestationResponse(
            attestation_object=base64url_to_bytes(
                requete.credential["response"]["attestationObject"]
            ),
            client_data_json=base64url_to_bytes(
                requete.credential["response"]["clientDataJSON"]
            ),
        ),
    )

    verification = verify_registration_response(
        credential=credential,
        expected_challenge=base64url_to_bytes(requete.challenge),
        expected_origin="http://localhost:3007",
        expected_rp_id="localhost",
    )

    reponse = verified_registration_to_dict(verification)
    log(__name__, f"reponse : {reponse}")


@auth.post("/initie")
def initie(
    requete: RequeteAuthentification,
    service_generation_de_challenge: ServiceAuthentification = Depends(  # type: ignore[assignment]
        fabrique_service_authentification
    ),
    entrepot_utilisateurs: EntrepotUtilisateurs = Depends(  # type: ignore[assignment]
        fabrique_entrepot_utilisateurs
    ),
):
    challenge = service_generation_de_challenge.genere_challenge()
    utilisateur = entrepot_utilisateurs.recupere_utilisateur_par_id_utilisateur(
        requete.utilisateur
    )
    if utilisateur is None:
        return Response(status_code=401)

    return {"challenge": challenge, "id": utilisateur.id}


@auth.post("/finalise")
def finalise(
    requete: RequeteAccreditation,
    reponse: Response,
    service_generation_de_challenge: ServiceAuthentification = Depends(  # type: ignore[assignment]
        fabrique_service_authentification
    ),
    service_generation_token: ServiceGenerationToken = Depends(  # type: ignore[assignment]
        fabrique_service_generation_token
    ),
    entrepot_utilisateurs: EntrepotUtilisateurs = Depends(  # type: ignore[assignment]
        fabrique_entrepot_utilisateurs
    ),
):
    utilisateur = entrepot_utilisateurs.recupere_utilisateur_par_id_de_clef(
        requete.credential.id
    )
    if utilisateur is None:
        reponse.status_code = 401
        return

    service_generation_de_challenge.verifie_challenge(
        requete.credential, requete.challenge, utilisateur.clef_publique
    )
    token = service_generation_token.genere_token()
    reponse.set_cookie(key="session", value=token, httponly=True, samesite="strict")
