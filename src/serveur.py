import secrets
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from infra.ui_kit.version_ui_kit import version_ui_kit

HEADERS_SECURITE = {
    "cross-origin-embedder-policy": "credentialless",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "expect-ct": "max-age=86400, enforce",
    "origin-agent-cluster": "?1",
    "strict-transport-security": "max-age=63072000; includeSubDomains; preload",
    "x-frame-options": "DENY",
    "x-content-type-options": "nosniff",
    "x-dns-prefetch-control": "off",
}


def fabrique_serveur(
    max_requetes_par_minute: int,
    static_root_directory="ui/dist/",
    la_version_ui_kit=version_ui_kit,
) -> FastAPI:
    serveur = FastAPI()

    limiteur = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{max_requetes_par_minute}/minute"],
    )
    serveur.state.limiter = limiteur
    # Les problèmes de types apparaissants ici sont connus ;
    # _c.f._ https://github.com/laurentS/slowapi/issues/188 .
    serveur.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore [arg-type]

    serveur.add_middleware(SlowAPIMiddleware)
    # Les problèmes de types apparaissants ici sont résolus côté `Starlette`, mais ne semblent pas encore avoir atteint `FastAPI` ;
    # _c.f._ https://github.com/Kludex/starlette/discussions/2451#discussioncomment-14855204 .
    serveur.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])  # type: ignore [arg-type]

    for static in ["assets", "fonts", "icons", "images"]:
        serveur.mount(
            f"/{static}", StaticFiles(directory=f"{static_root_directory}{static}")
        )

    @serveur.get("/")
    def index():
        return sert_la_page_statique(f"{static_root_directory}/index.html")

    def sert_la_page_statique(page_statique: str) -> HTMLResponse:
        nonce = secrets.token_hex(16)
        page_html = (
            Path(page_statique)
            .read_text(encoding="utf-8")
            .replace("%%NONCE_A_INJECTER%%", nonce)
            .replace("%%VERSION_UI_KIT%%", la_version_ui_kit())
            .replace("%%FAVICON%%", "/icons/favicon.ico")
        )
        response = HTMLResponse(content=page_html)
        headers = HEADERS_SECURITE | {
            "Content-Security-Policy": f"default-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com; style-src 'self' 'nonce-{nonce}' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com; script-src 'self' 'nonce-{nonce}'; img-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com",
            "Cross-Origin-Embedder-Policy": "credentialless",
        }
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        return response

    return serveur
