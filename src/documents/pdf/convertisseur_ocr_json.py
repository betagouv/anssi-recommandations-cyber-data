from __future__ import annotations

import base64
import json
import logging
import re
import time
from io import BytesIO
from pathlib import Path
from typing import Protocol

import pypdfium2
import requests

from documents.pdf.assembleur_blocs_json import (
    BlocOcr,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)
from documents.pdf.prompt_ocr_json import PROMPT_OCR_JSON


_log = logging.getLogger(__name__)


MODELE_OCR_PAR_DEFAUT = "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
ECHELLE_DE_RENDU_OCR = 1.5
NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR = 8000
TYPES_DE_BLOCS_OCR = {type_de_bloc.value for type_de_bloc in TypeDeBlocOcr}


def _valeur_nullable(type_json: str) -> dict[str, object]:
    return {"anyOf": [{"type": type_json}, {"type": "null"}]}


SCHEMA_BLOCS_OCR: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "blocks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string", "enum": sorted(TYPES_DE_BLOCS_OCR)},
                    "code": _valeur_nullable("string"),
                    "title": _valeur_nullable("string"),
                    "text": {"type": "string"},
                    "level": _valeur_nullable("integer"),
                    "continues_previous": {"type": "boolean"},
                    "items": {
                        "anyOf": [
                            {"type": "array", "items": {"type": "string"}},
                            {"type": "null"},
                        ]
                    },
                    "rows": {
                        "anyOf": [
                            {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            {"type": "null"},
                        ]
                    },
                },
                "required": [
                    "type",
                    "code",
                    "title",
                    "text",
                    "level",
                    "continues_previous",
                    "items",
                    "rows",
                ],
            },
        }
    },
    "required": ["blocks"],
}


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


class RendeurDePagePdf(Protocol):
    def nombre_de_pages(self, chemin: str | Path) -> int:
        ...

    def encode_l_image(self, chemin: str | Path, numero_page: int) -> str:
        ...


class ConvertisseurDePagesOcrJson(Protocol):
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


class RendeurDePagePdfPypdfium2:
    def nombre_de_pages(self, chemin: str | Path) -> int:
        document_pdf = self._ouvre_le_pdf(chemin)
        try:
            return len(document_pdf)
        finally:
            document_pdf.close()

    def encode_l_image(self, chemin: str | Path, numero_page: int) -> str:
        document_pdf = self._ouvre_le_pdf(chemin)
        try:
            image = document_pdf[numero_page - 1].render(
                scale=ECHELLE_DE_RENDU_OCR
            ).to_pil()
            with BytesIO() as flux:
                image.save(flux, format="PNG")
                return base64.b64encode(flux.getvalue()).decode("ascii")
        finally:
            document_pdf.close()

    @staticmethod
    def _ouvre_le_pdf(chemin: str | Path):
        chemin_pdf = Path(chemin)
        if chemin_pdf.exists():
            return pypdfium2.PdfDocument(chemin_pdf)
        reponse = requests.get(str(chemin), timeout=30)
        reponse.raise_for_status()
        return pypdfium2.PdfDocument(BytesIO(reponse.content))


class ConvertisseurOcrJson:
    def __init__(
        self,
        cle_api: str,
        url_albert: str,
        modele: str = MODELE_OCR_PAR_DEFAUT,
        delai: int = 180,
        transport_http: TransportHttp | None = None,
        rendeur_de_page: RendeurDePagePdf | None = None,
    ):
        self.cle_api = cle_api
        self.url_albert = url_albert.rstrip("/")
        self.modele = modele
        self.delai = delai
        self.transport_http = transport_http or TransportHttpAlbert()
        self.rendeur_de_page = rendeur_de_page or RendeurDePagePdfPypdfium2()

    def convertit(
        self,
        chemin: str | Path,
        plages_de_pages: list[tuple[int, int]] | None,
    ) -> ResultatOcrPdf:
        nombre_de_pages = self.rendeur_de_page.nombre_de_pages(chemin)
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
                    self.rendeur_de_page.encode_l_image(chemin, numero_page)
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
        if not isinstance(annotation, dict) or not isinstance(
            annotation.get("blocks"), list
        ):
            raise ErreurOcrJson("La sortie OCR ne contient pas de liste de blocs")

        blocs_ocr: list[BlocOcr] = []
        for bloc_json in annotation["blocks"]:
            if not isinstance(bloc_json, dict):
                raise ErreurOcrJson("Un bloc OCR n'est pas un objet JSON")
            champs_obligatoires = {
                "type",
                "code",
                "title",
                "text",
                "level",
                "continues_previous",
                "items",
                "rows",
            }
            if champs_obligatoires - bloc_json.keys():
                raise ErreurOcrJson("Un bloc OCR ne contient pas toutes ses propriétés")
            type_de_bloc = bloc_json["type"]
            if type_de_bloc not in TYPES_DE_BLOCS_OCR:
                raise ErreurOcrJson("Un bloc OCR possède un type inconnu")
            code = bloc_json["code"]
            if code == "":
                code = None
            if code is not None and not isinstance(code, str):
                raise ErreurOcrJson("Un code de recommandation OCR est invalide")
            titre = bloc_json["title"]
            if titre == "":
                titre = None
            texte = bloc_json["text"]
            niveau = bloc_json["level"]
            est_une_continuation = bloc_json["continues_previous"]
            elements_de_liste = bloc_json["items"]
            lignes_de_tableau = bloc_json["rows"]
            if not isinstance(titre, (str, type(None))) or not isinstance(texte, str):
                raise ErreurOcrJson("Le titre ou le texte d'un bloc OCR est invalide")
            if type_de_bloc == TypeDeBlocOcr.RECOMMANDATION.value and code:
                code_normalise = re.fullmatch(r"(R\d+)-*", code)
                if code_normalise is not None:
                    code = code_normalise.group(1)
                else:
                    texte = "\n".join(
                        partie for partie in (code, titre, texte) if partie
                    )
                    type_de_bloc = TypeDeBlocOcr.AUTRE.value
                    code = None
                    titre = None
            if type_de_bloc != TypeDeBlocOcr.RECOMMANDATION.value:
                code = None
            if type_de_bloc != TypeDeBlocOcr.TITRE.value:
                niveau = None
            if niveau is not None and (
                isinstance(niveau, bool) or not isinstance(niveau, int)
            ):
                raise ErreurOcrJson("Le niveau d'un bloc OCR est invalide")
            if not isinstance(est_une_continuation, bool):
                raise ErreurOcrJson("La continuation d'un bloc OCR est invalide")
            if elements_de_liste is not None and (
                not isinstance(elements_de_liste, list)
                or not all(isinstance(element, str) for element in elements_de_liste)
            ):
                raise ErreurOcrJson("Les éléments de liste d'un bloc OCR sont invalides")
            if lignes_de_tableau is not None and (
                not isinstance(lignes_de_tableau, list)
                or not all(
                    isinstance(ligne, list)
                    and all(isinstance(cellule, str) for cellule in ligne)
                    for ligne in lignes_de_tableau
                )
            ):
                raise ErreurOcrJson("Les lignes de tableau d'un bloc OCR sont invalides")
            blocs_ocr.append(
                BlocOcr(
                    type_de_bloc=TypeDeBlocOcr(type_de_bloc),
                    code=code,
                    titre=titre,
                    texte=texte,
                    niveau=niveau,
                    est_une_continuation=est_une_continuation,
                    elements_de_liste=tuple(elements_de_liste or ()),
                    lignes_de_tableau=tuple(
                        tuple(ligne) for ligne in (lignes_de_tableau or ())
                    ),
                )
            )
        return blocs_ocr
