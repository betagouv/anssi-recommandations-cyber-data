from fastapi import APIRouter, Response
from fastapi.params import Depends
from pydantic import BaseModel

from adaptateurs.authentification import (
    fabrique_service_authentification,
    ServiceAuthentification,
    EntrepotUtilisateurs,
    fabrique_entrepot_utilisateurs,
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


@auth.post("/auth/finish")
def finish(assertion):
    # credential = admins["credential_id"]
    #
    # verify_authentication_response(
    #     credential=credential,
    #     assertion=assertion,
    #     expected_challenge=sessions["challenge"],
    #     expected_origin="https://admin.example.com"
    # )
    #
    # return {
    #     "authenticated": True
    # }
    pass
