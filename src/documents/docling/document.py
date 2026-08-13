import json
from typing import Optional

from docling_core.types import DoclingDocument

from documents.elements_filtres import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.indexeur.indexeur import DocumentAIndexer
from documents.page import Page, BlocPage
from documents.pdf.modeles_ocr_json import ErreurPageOcr


LONGUEUR_MAXIMALE_D_UNE_METADATA = 255


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
                metadata["titre"] = bloc.contexte.titre[:LONGUEUR_MAXIMALE_D_UNE_METADATA]
            if bloc.contexte.chemin_des_sections:
                metadata["chemin_sections"] = json.dumps(
                    list(bloc.contexte.chemin_des_sections), ensure_ascii=False
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
