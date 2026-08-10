from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Protocol

import requests
from pydantic import ValidationError

from documents.pdf.assembleur_blocs_json import (
    BlocOcr,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)
from documents.pdf._contrat_ocr_json import SCHEMA_BLOCS_OCR, _ReponseOcrJson
from documents.pdf._rendeur_pages_pdf import (
    RendeurDePagesPdf,
    RendeurDePagesPdfPypdfium2,
)
from documents.pdf.prompt_ocr_json import PROMPT_OCR_JSON


_log = logging.getLogger(__name__)


MODELE_OCR_PAR_DEFAUT = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
DELAI_MAXIMAL_OCR = 300
NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR = 8000


class ErreurOcrJson(RuntimeError):
    pass


class ReponseHttp(Protocol):
    status_code: int

    def json(self) -> object:
        ...


class TransportHttp(Protocol):
    def post(
        self,
        url: str,
        headers: dict[str, str],
        corps: dict[str, object],
        timeout: int,
    ) -> ReponseHttp:
        ...


class ExtracteurDeBlocsOcr(Protocol):
    def convertit(
        self,
        chemin: str | Path,
        plages_de_pages: list[tuple[int, int]] | None,
    ) -> ResultatOcrPdf:
        ...


class TransportHttpAlbert:
    def post(
        self,
        url: str,
        headers: dict[str, str],
        corps: dict[str, object],
        timeout: int,
    ) -> requests.Response:
        return requests.post(url, headers=headers, json=corps, timeout=timeout)

class ExtracteurDeBlocsOcrDepuisUnPdf:
    def __init__(
        self,
        cle_api: str,
        url_albert: str,
        modele: str = MODELE_OCR_PAR_DEFAUT,
        delai: int = DELAI_MAXIMAL_OCR,
        transport_http: TransportHttp | None = None,
        rendeur_de_pages: RendeurDePagesPdf | None = None,
    ):
        self.cle_api = cle_api
        self.url_albert = url_albert.rstrip("/")
        self.modele = modele
        self.delai = delai
        self.transport_http = transport_http or TransportHttpAlbert()
        self.rendeur_de_pages = rendeur_de_pages or RendeurDePagesPdfPypdfium2()

    def convertit(
        self,
        chemin: str | Path,
        plages_de_pages: list[tuple[int, int]] | None,
    ) -> ResultatOcrPdf:
        nombre_de_pages = self.rendeur_de_pages.nombre_de_pages(chemin)
        pages_a_ocr = self._determine_les_pages_a_ocr(
            nombre_de_pages,
            plages_de_pages,
        )
        pages_ocr = []
        for numero_page in pages_a_ocr:
            _log.info("Début OCR de la page %s/%s", numero_page, nombre_de_pages)
            debut_ocr = time.perf_counter()
            blocs_ocr = self._decode_les_blocs(
                self._appelle_ocr(
                    self.rendeur_de_pages.encode_l_image(chemin, numero_page)
                )
            )
            _log.info(
                "Fin OCR de la page %s/%s en %.1f secondes",
                numero_page,
                nombre_de_pages,
                time.perf_counter() - debut_ocr,
            )
            pages_ocr.append(PageOcr(numero_page=numero_page, blocs=tuple(blocs_ocr)))
        return ResultatOcrPdf(nombre_de_pages=nombre_de_pages, pages=tuple(pages_ocr))

    @staticmethod
    def _determine_les_pages_a_ocr(
        nombre_de_pages: int,
        plages_de_pages: list[tuple[int, int]] | None,
    ) -> tuple[int, ...]:
        if plages_de_pages is None:
            return tuple(range(1, nombre_de_pages + 1))
        return tuple(
            numero_page
            for page_debut, page_fin in plages_de_pages
            for numero_page in range(page_debut, page_fin + 1)
        )

    def _appelle_ocr(self, image_base64: str) -> object:
        try:
            reponse_http = self.transport_http.post(
                f"{self.url_albert}/chat/completions",
                {"Authorization": f"Bearer {self.cle_api}"},
                self._construit_la_requete(image_base64),
                self.delai,
            )
        except Exception as erreur:
            raise ErreurOcrJson("Échec de l'appel OCR") from erreur

        if reponse_http.status_code != 200:
            raise ErreurOcrJson("La réponse OCR est en erreur")
        try:
            corps = reponse_http.json()
            contenu = self._extrait_le_contenu_de_la_reponse(corps)
            return json.loads(contenu) if isinstance(contenu, str) else contenu
        except (KeyError, IndexError, TypeError, ValueError) as erreur:
            raise ErreurOcrJson("La réponse OCR ne contient pas de JSON exploitable") from erreur

    @staticmethod
    def _extrait_le_contenu_de_la_reponse(corps: object) -> object:
        if not isinstance(corps, dict):
            raise TypeError
        choix = corps.get("choices")
        if not isinstance(choix, list) or not choix:
            raise KeyError("choices")
        premier_choix = choix[0]
        if not isinstance(premier_choix, dict):
            raise TypeError
        message = premier_choix.get("message")
        if not isinstance(message, dict) or "content" not in message:
            raise KeyError("message.content")
        return message["content"]

    def _construit_la_requete(self, image_base64: str) -> dict[str, object]:
        return {
            "model": self.modele,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                        {"type": "text", "text": PROMPT_OCR_JSON},
                    ],
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "blocs_page",
                    "description": "Blocs structurés d'une page.",
                    "strict": True,
                    "schema": SCHEMA_BLOCS_OCR,
                },
            },
            "temperature": 0,
            "max_completion_tokens": NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR,
        }

    @staticmethod
    def _decode_les_blocs(annotation: object) -> list[BlocOcr]:
        try:
            reponse_ocr = _ReponseOcrJson.model_validate(annotation)
        except ValidationError as erreur:
            raise ErreurOcrJson("La sortie OCR ne respecte pas le contrat JSON") from erreur

        blocs_ocr: list[BlocOcr] = []
        for bloc_json in reponse_ocr.blocs:
            type_de_bloc = bloc_json.type_de_bloc.value
            code = bloc_json.code_recommandation
            if code == "":
                code = None
            titre = bloc_json.titre
            if titre == "":
                titre = None
            texte = bloc_json.texte
            niveau = bloc_json.niveau
            est_une_continuation = bloc_json.est_une_continuation
            elements_de_liste = bloc_json.elements_de_liste
            if type_de_bloc == TypeDeBlocOcr.RECOMMANDATION.value:
                code_normalise = re.fullmatch(r"(R\d+)-*", code) if code else None
                if code is None:
                    type_de_bloc = TypeDeBlocOcr.LISTE.value
                elif code_normalise is None:
                    texte = "\n".join(
                        partie for partie in (code, titre, texte) if partie
                    )
                    type_de_bloc = TypeDeBlocOcr.AUTRE.value
                    code = None
                    titre = None
                else:
                    code = code_normalise.group(1)
            if type_de_bloc != TypeDeBlocOcr.RECOMMANDATION.value:
                code = None
            niveau = ExtracteurDeBlocsOcrDepuisUnPdf._normalise_le_niveau(
                type_de_bloc, niveau
            )
            blocs_ocr.append(
                BlocOcr(
                    type_de_bloc=TypeDeBlocOcr(type_de_bloc),
                    code=code,
                    titre=titre,
                    texte=texte,
                    niveau=niveau,
                    est_une_continuation=est_une_continuation,
                    elements_de_liste=tuple(elements_de_liste or ()),
                )
            )
        return blocs_ocr

    @staticmethod
    def _normalise_le_niveau(type_de_bloc: object, niveau: object) -> int | None:
        if type_de_bloc != TypeDeBlocOcr.TITRE.value or niveau == 0:
            return None
        if niveau is not None and (
            isinstance(niveau, bool) or not isinstance(niveau, int)
        ):
            raise ErreurOcrJson("Le niveau d'un bloc OCR est invalide")
        return niveau
