import base64
from typing import Any

from fastapi import APIRouter, Response, Request
from fastapi.params import Depends
from pydantic import BaseModel
from webauthn import options_to_json
from webauthn.helpers import base64url_to_bytes

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

auth = APIRouter(prefix="/auth")


class RequeteAuthentification(BaseModel):
    utilisateur: str


class RequeteVerificationEnrolement(BaseModel):
    credential: dict[str, Any]
    utilisateur: str


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
    request: Request,
    requete: RequeteEnrolement,
    service_authentification: ServiceAuthentification = Depends(  # type: ignore[assignment]
        fabrique_service_authentification
    ),
):
    options = service_authentification.initie_enrolement(requete.utilisateur)
    service_authentification.persiste_le_challenge(
        request, requete.utilisateur, options.challenge
    )

    return {"options": options_to_json(options)}


@auth.post("/verifie-enrolement")
def verifie_enrolement(
    request: Request,
    requete: RequeteVerificationEnrolement,
    service_authentification: ServiceAuthentification = Depends(  # type: ignore[assignment]
        fabrique_service_authentification
    ),
):
    challenge = service_authentification.recupere_challenge(
        request, requete.utilisateur
    )
    reponse = verified_registration_to_dict(
        service_authentification.verifie_enrolement(requete.credential, challenge)
    )
    log(__name__, f"Finalisation de l'enrôlement : {reponse}")


@auth.post("/initie")
def initie(
    request: Request,
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

    service_generation_de_challenge.persiste_le_challenge(
        request, requete.utilisateur, base64url_to_bytes(challenge)
    )
    return {"challenge": challenge, "id": utilisateur.id}


@auth.post("/finalise")
def finalise(
    request: Request,
    requete: RequeteAccreditation,
    reponse: Response,
    service_authentification: ServiceAuthentification = Depends(  # type: ignore[assignment]
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

    challenge = service_authentification.recupere_challenge(
        request, requete.utilisateur
    )
    service_authentification.verifie_challenge(
        requete.credential, challenge, utilisateur.clef_publique
    )
    token = service_generation_token.genere_token()
    reponse.set_cookie(key="session", value=token, httponly=True, samesite="strict")
