import jwt
from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from configuration import recupere_configuration


def fabrique_verifie_token_jwt():
    return verifie_token_jwt


security = HTTPBearer(auto_error=False)


def verifie_token_jwt(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    secret=recupere_configuration().secret_jwt,
):
    cookies = request.cookies if request is not None else {}
    if "session" in cookies:
        token = cookies["session"]
        _decode_token(secret, token)
        return token

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
        )

    token = credentials.credentials
    _decode_token(secret, token)
    return token


def _decode_token(secret: str, token: str):
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.exceptions.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )
