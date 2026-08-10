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
ECHELLE_DE_RENDU_OCR = 3.0
DELAI_MAXIMAL_OCR = 300
NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR = 8000
TYPES_DE_BLOCS_OCR = {type_de_bloc.value for type_de_bloc in TypeDeBlocOcr}


def _valeur_nullable(type_json: str) -> dict[str, object]:
    return {"anyOf": [{"type": type_json}, {"type": "null"}]}


SCHEMA_BLOCS_OCR: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "blocs": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type_de_bloc": {"type": "string", "enum": sorted(TYPES_DE_BLOCS_OCR)},
                    "code_recommandation": _valeur_nullable("string"),
                    "titre": _valeur_nullable("string"),
                    "texte": {"type": "string"},
                    "niveau": _valeur_nullable("integer"),
                    "est_une_continuation": {"type": "boolean"},
                    "elements_de_liste": {
                        "anyOf": [
                            {"type": "array", "items": {"type": "string"}},
                            {"type": "null"},
                        ]
                    },
                    "lignes_de_tableau": {
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
                    "type_de_bloc",
                    "code_recommandation",
                    "titre",
                    "texte",
                    "niveau",
                    "est_une_continuation",
                    "elements_de_liste",
                    "lignes_de_tableau",
                ],
            },
        }
    },
    "required": ["blocs"],
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
        delai: int = DELAI_MAXIMAL_OCR,
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
            annotation.get("blocs"), list
        ):
            raise ErreurOcrJson("La sortie OCR ne contient pas de liste de blocs")

        blocs_ocr: list[BlocOcr] = []
        for bloc_json in annotation["blocs"]:
            if not isinstance(bloc_json, dict):
                raise ErreurOcrJson("Un bloc OCR n'est pas un objet JSON")
            champs_obligatoires = {
                "type_de_bloc",
                "code_recommandation",
                "titre",
                "texte",
                "niveau",
                "est_une_continuation",
                "elements_de_liste",
                "lignes_de_tableau",
            }
            if champs_obligatoires - bloc_json.keys():
                raise ErreurOcrJson("Un bloc OCR ne contient pas toutes ses propriétés")
            type_de_bloc = bloc_json["type_de_bloc"]
            if type_de_bloc not in TYPES_DE_BLOCS_OCR:
                raise ErreurOcrJson("Un bloc OCR possède un type inconnu")
            code = bloc_json["code_recommandation"]
            if code == "":
                code = None
            if code is not None and not isinstance(code, str):
                raise ErreurOcrJson("Un code de recommandation OCR est invalide")
            titre = bloc_json["titre"]
            if titre == "":
                titre = None
            texte = bloc_json["texte"]
            niveau = bloc_json["niveau"]
            est_une_continuation = bloc_json["est_une_continuation"]
            elements_de_liste = bloc_json["elements_de_liste"]
            lignes_de_tableau = bloc_json["lignes_de_tableau"]
            if not isinstance(titre, (str, type(None))) or not isinstance(texte, str):
                raise ErreurOcrJson("Le titre ou le texte d'un bloc OCR est invalide")
            if type_de_bloc == TypeDeBlocOcr.RECOMMANDATION.value:
                if code is None:
                    type_de_bloc = TypeDeBlocOcr.LISTE.value
                else:
                    code_normalise = re.fullmatch(r"(R\d+)-*", code)
                    if code_normalise is None:
                        raise ErreurOcrJson(
                            "Un code de recommandation OCR est invalide"
                        )
                    code = code_normalise.group(1)
            if type_de_bloc != TypeDeBlocOcr.RECOMMANDATION.value:
                code = None
            niveau = ConvertisseurOcrJson._normalise_le_niveau(type_de_bloc, niveau)
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

    @staticmethod
    def _normalise_le_niveau(type_de_bloc: object, niveau: object) -> int | None:
        if type_de_bloc != TypeDeBlocOcr.TITRE.value or niveau == 0:
            return None
        if niveau is not None and (
            isinstance(niveau, bool) or not isinstance(niveau, int)
        ):
            raise ErreurOcrJson("Le niveau d'un bloc OCR est invalide")
        return niveau
