import time

import jwt
import pytest
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import empty_receive, empty_send
from starlette.types import Scope

from api.securite import verifie_token_jwt

SECRET_JWT = "un_secret_tres_secret"


class ScopeDeTest(Scope):
    def __init__(self):
        self._data = {"type": "http"}

    def __setitem__(self, key, value, /):
        self._data[key] = value

    def __delitem__(self, key, /):
        del self._data[key]

    def __getitem__(self, key, /):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


class RequestDeTest(Request):
    def __init__(self, cookies: dict[str, str]):
        super().__init__(ScopeDeTest(), empty_receive, empty_send)
        self._cookies = cookies

    @property
    def cookies(self) -> dict[str, str]:
        return self._cookies


def test_verifie_token_jwt_leve_exception_si_signature_invalide():
    token_invalide = jwt.encode(
        {"some": "payload"}, "mauvais_secret", algorithm="HS256"
    )
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_invalide
    )

    with pytest.raises(HTTPException) as excinfo:
        verifie_token_jwt(None, credentials, SECRET_JWT)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token invalide"


def test_verifie_token_jwt_accepte_token_valide():
    token_valide = jwt.encode({"some": "payload"}, SECRET_JWT, algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_valide
    )

    token = verifie_token_jwt(None, credentials, SECRET_JWT)

    assert token == token_valide


def test_verifie_token_jwt_leve_exception_si_token_expire():
    payload_expire = {"some": "payload", "exp": time.time() - 10}
    token_expire = jwt.encode(payload_expire, SECRET_JWT, algorithm="HS256")
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token_expire
    )

    with pytest.raises(HTTPException) as excinfo:
        verifie_token_jwt(None, credentials, SECRET_JWT)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token invalide"


def test_verifie_token_jwt_lorsque_present_dans_un_cookie_de_session():
    token_valide = jwt.encode({"some": "payload"}, SECRET_JWT, algorithm="HS256")
    request = RequestDeTest({"session": token_valide})

    token = verifie_token_jwt(request, None, SECRET_JWT)

    assert token == token_valide
