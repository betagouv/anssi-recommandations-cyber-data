import time

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.securite import verifie_token_jwt

SECRET_JWT = "un_secret_tres_secret"


@pytest.fixture(autouse=True)
def definit_secret_jwt(monkeypatch):
    monkeypatch.setenv("SECRET_JWT", SECRET_JWT)


def test_verifie_token_jwt_leve_exception_si_signature_invalide():
    token_invalide = jwt.encode(
        {"some": "payload"}, "mauvais_secret", algorithm="HS256"
    )
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_invalide
    )

    with pytest.raises(HTTPException) as excinfo:
        verifie_token_jwt(credentials)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token invalide"


def test_verifie_token_jwt_accepte_token_valide():
    token_valide = jwt.encode({"some": "payload"}, SECRET_JWT, algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_valide
    )

    token = verifie_token_jwt(credentials)

    assert token == token_valide


def test_verifie_token_jwt_leve_exception_si_token_expire():
    payload_expire = {"some": "payload", "exp": time.time() - 10}
    token_expire = jwt.encode(payload_expire, SECRET_JWT, algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_expire
    )

    with pytest.raises(HTTPException) as excinfo:
        verifie_token_jwt(credentials)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token invalide"
