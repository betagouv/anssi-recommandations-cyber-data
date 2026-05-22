from pathlib import Path
from typing import NamedTuple

from adaptateurs.clients_albert import ClientAlbertIndexation
from configuration import MSC, recupere_configuration
from documents.collecte.collecte import (
    collecte_document_maitrise,
    collecte_documents_distants,
    mappe_en_document_distant,
)
from documents.indexe_documents_rag import fabrique_client_albert
from documents.indexeur.indexeur import (
    DocumentAIndexer,
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
    ReponseDocumentMaitriseEnSucces,
)
from documents.pdf.cree_document_pdf import normalise_url
from documents.pdf.document_pdf import DocumentPDFDistant
from infra.logger import log
from jeopardy.service import ServiceJeopardyse, CollectionEntiere
from jeopardy.service_jeopardyse_collection_entiere import (
    fabrique_service_jeopardise_collection_entiere,
)


FICHIER_DOCUMENTS_DISTANTS = "donnees/documents_distants.json"
FICHIER_DOCUMENTS_MAITRISES = (
    "donnees/collection_reponses_maitrisees/faq_reponses_maitrisees.html"
)


class DocumentsSources(NamedTuple):
    fichiers: list[str] = []


class CollecteurDocumentsAdditionnels:
    def collecte(self) -> list[DocumentAIndexer]:
        docs: list[DocumentAIndexer] = []
        mapping = mappe_en_document_distant(Path(FICHIER_DOCUMENTS_DISTANTS))
        if mapping is not None:
            docs += collecte_documents_distants(mapping)
        doc_maitrise = collecte_document_maitrise(Path(FICHIER_DOCUMENTS_MAITRISES))
        if doc_maitrise is not None:
            docs.append(doc_maitrise)
        return docs


class ServiceIndexationNouvellesCollections:
    def __init__(
        self,
        client_indexation: ClientAlbertIndexation,
        configuration_MSC: MSC,
        service_jeopardy: ServiceJeopardyse,
        collecteur: CollecteurDocumentsAdditionnels = CollecteurDocumentsAdditionnels(),
    ):
        super().__init__()
        self._service_jeopardy = service_jeopardy
        self._client_indexation = client_indexation
        self._configuration_MSC = configuration_MSC
        self._collecteur = collecteur

    def indexe_documents(
        self,
        nom: str,
        description: str,
        sources: DocumentsSources,
    ):
        reponse_collection = self._client_indexation.cree_collection(nom, description)
        log(
            __name__,
            f"Collection {nom} créée avec succès (id : {reponse_collection.id})",
        )
        self._client_indexation.attribue_collection(reponse_collection.id)

        docs: list[DocumentAIndexer] = [
            DocumentPDFDistant(doc, normalise_url(doc, self._configuration_MSC))
            for doc in sources.fichiers
        ]
        docs += self._collecteur.collecte()

        log(__name__, f"Indexe {len(docs)} documents")

        resultats = self._client_indexation.ajoute_documents(docs)

        les_documents_en_erreur = list(
            filter(
                lambda reponse: isinstance(reponse, ReponseDocumentEnErreur), resultats
            )
        )
        les_documents_en_succes = list(
            filter(
                lambda reponse: isinstance(
                    reponse, (ReponseDocumentEnSucces, ReponseDocumentMaitriseEnSucces)
                ),
                resultats,
            )
        )

        log(
            __name__,
            f"{len(les_documents_en_succes)} documents ajoutés à la collection {reponse_collection.id}",
        )
        log(
            __name__,
            f"{len(les_documents_en_erreur)} documents non ajoutés à la collection",
        )

        self._service_jeopardy.jeopardyse(
            CollectionEntiere(
                id_collection=reponse_collection.id,
                nom_collection=f"Jeopardy - {nom}",
                description_collection=description,
            )
        )
        return resultats


def fabrique_service_indexation_collections() -> ServiceIndexationNouvellesCollections:
    configuration = recupere_configuration()
    return ServiceIndexationNouvellesCollections(
        fabrique_client_albert(),
        configuration.msc,
        fabrique_service_jeopardise_collection_entiere(),
    )
