import json
from typing import Optional

from docling_core.types import DoclingDocument

from documents.elements_filtres import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.indexeur.indexeur import DocumentAIndexer
from documents.page import Page, BlocPage
from documents.pdf.modeles_ocr_json import ErreurPageOcr


LONGUEUR_MAXIMALE_D_UNE_METADATA = 255
MARQUEUR_SECTIONS_OMISES = "…"


def _tronque_une_section(section: str, longueur_maximale: int) -> str:
    if len(section) <= longueur_maximale:
        return section
    if longueur_maximale <= 0:
        return ""
    if longueur_maximale == 1:
        return MARQUEUR_SECTIONS_OMISES

    longueur_avant = (longueur_maximale - 1) // 2
    longueur_apres = longueur_maximale - longueur_avant - 1
    return (
        section[:longueur_avant] + MARQUEUR_SECTIONS_OMISES + section[-longueur_apres:]
    )


def _serialise_chemin_sections(chemin_sections: tuple[str, ...]) -> str:
    chemin = json.dumps(list(chemin_sections), ensure_ascii=False)
    if len(chemin) <= LONGUEUR_MAXIMALE_D_UNE_METADATA:
        return chemin

    if len(chemin_sections) == 1:
        sections_resumees = [chemin_sections[0]]
    elif len(chemin_sections) == 2:
        sections_resumees = list(chemin_sections)
    else:
        sections_resumees = [
            chemin_sections[0],
            MARQUEUR_SECTIONS_OMISES,
            chemin_sections[-1],
        ]

    serialisation = json.dumps(sections_resumees, ensure_ascii=False)
    while len(serialisation) > LONGUEUR_MAXIMALE_D_UNE_METADATA:
        indices_tronquables = [
            index
            for index, section in enumerate(sections_resumees)
            if section != MARQUEUR_SECTIONS_OMISES and len(section) > 1
        ]
        if not indices_tronquables:
            break

        index = max(
            indices_tronquables, key=lambda indice: len(sections_resumees[indice])
        )
        exces = len(serialisation) - LONGUEUR_MAXIMALE_D_UNE_METADATA
        longueur_cible = max(1, len(sections_resumees[index]) - exces)
        if longueur_cible == len(sections_resumees[index]):
            longueur_cible -= 1
        sections_resumees[index] = _tronque_une_section(
            sections_resumees[index], longueur_cible
        )
        serialisation = json.dumps(sections_resumees, ensure_ascii=False)

    return serialisation


class Document:
    def __init__(
        self, document_a_indexer: DocumentAIndexer, reponse_maitrisee: bool = False
    ):
        super().__init__()
        self._nom_document = document_a_indexer.nom_document
        self._url = document_a_indexer.url
        self._reponse_maitrisee = reponse_maitrisee
        self.pages: dict[int, Page] = {}
        self.erreurs_pages: tuple[ErreurPageOcr, ...] = ()

    @property
    def nom_document(self):
        return self._nom_document

    @property
    def url(self):
        return self._url

    def metadata(self, bloc: BlocPage) -> dict:
        metadata = {
            "source_url": self.url,
            "page": bloc.numero_page if bloc.numero_page is not None else 0,
            "nom_document": self.nom_document,
        }
        if bloc.position_page is not None:
            metadata["position_page"] = bloc.position_page
        if bloc.derniere_page is not None:
            metadata["derniere_page"] = bloc.derniere_page
        if bloc.contexte is not None:
            if bloc.contexte.type_de_bloc is not None:
                metadata["type_de_bloc"] = bloc.contexte.type_de_bloc
            if bloc.contexte.code_recommandation is not None:
                metadata["code_recommandation"] = bloc.contexte.code_recommandation
            if bloc.contexte.titre is not None:
                metadata["titre"] = bloc.contexte.titre[
                    :LONGUEUR_MAXIMALE_D_UNE_METADATA
                ]
            if bloc.contexte.chemin_des_sections:
                metadata["chemin_sections"] = _serialise_chemin_sections(
                    bloc.contexte.chemin_des_sections
                )
            if bloc.contexte.niveau is not None:
                metadata["niveau"] = bloc.contexte.niveau
        if self._reponse_maitrisee:
            metadata["reponse_maitrisee"] = True
        if hasattr(bloc, "id_reponse") and bloc.id_reponse:
            metadata["id_reponse"] = bloc.id_reponse
        return metadata

    def genere_les_pages(
        self,
        generateur: GenerateurDePages,
        elements_filtres: ElementsFiltres,
        document: Optional[DoclingDocument],
    ):
        self.pages = generateur.genere(elements_filtres, document)
