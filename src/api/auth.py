from fastapi import APIRouter, Response
from fastapi.params import Depends
from pydantic import BaseModel

from adaptateurs.authentification import (
    fabrique_service_authentification,
    ServiceAuthentification,
    EntrepotUtilisateurs,
    fabrique_entrepot_utilisateurs,
    RequeteAccreditation,
    fabrique_service_generation_token,
    ServiceGenerationToken,
)

auth = APIRouter(prefix="/auth")


class RequeteAuthentification(BaseModel):
    utilisateur: str


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
        return Response(status_code=401)

    service_generation_de_challenge.verifie_challenge(
        requete.credential, requete.challenge, utilisateur.clef_publique
    )
    service_generation_token.genere_token()
