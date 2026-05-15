import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from configuration import recupere_configuration


def fabrique_verifie_token_jwt():
    return verifie_token_jwt


security = HTTPBearer()


def verifie_token_jwt(
    credentials: HTTPAuthorizationCredentials = Security(security),
    secret=recupere_configuration().secret_jwt,
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
        )

    token = credentials.credentials

    try:
        jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.exceptions.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )

    return token
