from adaptateurs.clients_albert import ClientAlbertIndexation
from configuration import recupere_configuration, MSC, CollectionsMQC
from documents.html.document_html import DocumentHTML
from documents.indexe_documents_rag import fabrique_client_albert
from documents.indexeur.indexeur import DocumentAIndexer
from documents.indexeur.indexeur import (
    ReponseDocument,
    ReponseDocumentEnSucces,
    ReponseDocumentMaitriseEnSucces,
    ReponseDocumentIndexePartiellement,
)
from documents.pdf.cree_document_pdf import normalise_url
from documents.pdf.document_pdf import DocumentPDFDistant
from jeopardy.service import ServiceJeopardyse, ListeDeDocuments
from jeopardy.service_jeopardyse_liste_de_documents import (
    fabrique_service_jeopardise_documents,
)


class ServiceIndexationNouveauxDocuments:
    def __init__(
        self,
        client_indexation: ClientAlbertIndexation,
        collections_MQC: CollectionsMQC,
        configuration_MSC: MSC,
        service_jeopardy: ServiceJeopardyse,
    ):
        super().__init__()
        self._service_jeopardy = service_jeopardy
        self._id_collection = collections_MQC.id_collection_indexee
        self._id_collection_jeopardy = collections_MQC.id_collection_jeopardy
        self._client_indexation = client_indexation
        self._configuration_MSC = configuration_MSC

    def indexe_documents(
        self,
        documents: list[str],
        documents_a_supprimer: list[str] = [],
        url_a_ajouter: str | None = None,
    ) -> list[ReponseDocument]:
        self._client_indexation.attribue_collection(self._id_collection)
        documents_a_indexer: list[DocumentAIndexer] = [
            DocumentPDFDistant(document, normalise_url(document, self._configuration_MSC))
            for document in documents
        ]
        if url_a_ajouter:
            nom_document = url_a_ajouter.rstrip("/").rsplit("/", 1)[-1]
            documents_a_indexer.append(DocumentHTML(nom_document, url_a_ajouter))

        documents_indexes: list[DocumentAIndexer] = []
        for document in documents_a_indexer:
            try:
                identifiant_document_existant = self._client_indexation.document_existe(
                    document.nom_document, self._id_collection
                )
                if identifiant_document_existant:
                    self._client_indexation.supprime_document(
                        identifiant_document_existant
                    )
                identifiant_document_jeopardy_existant = (
                    self._client_indexation.document_existe(
                        document.nom_document, self._id_collection_jeopardy
                    )
                )
                if identifiant_document_jeopardy_existant:
                    self._client_indexation.supprime_document(
                        identifiant_document_jeopardy_existant
                    )
                documents_indexes.append(document)
            except Exception:
                continue
        resultats: list[ReponseDocument] = self._client_indexation.ajoute_documents(
            documents_indexes
        )
        noms_documents_indexes = [
            (
                resultat.nom
                if isinstance(resultat, ReponseDocumentIndexePartiellement)
                else resultat.name
            )
            for resultat in resultats
            if isinstance(
                resultat,
                (
                    ReponseDocumentEnSucces,
                    ReponseDocumentMaitriseEnSucces,
                    ReponseDocumentIndexePartiellement,
                ),
            )
        ]
        if noms_documents_indexes:
            self._service_jeopardy.jeopardyse(
                ListeDeDocuments(
                    noms_documents=noms_documents_indexes,
                    id_collection_jeopardy=self._id_collection_jeopardy,
                    id_collection_mqc=self._id_collection,
                )
            )
        for document_a_supprimer in documents_a_supprimer:
            identifiant_document_existant = self._client_indexation.document_existe(
                document_a_supprimer, self._id_collection
            )
            if identifiant_document_existant:
                self._client_indexation.supprime_document(identifiant_document_existant)

            identifiant_document_jeopardy_existant = (
                self._client_indexation.document_existe(
                    document_a_supprimer, self._id_collection_jeopardy
                )
            )

            if identifiant_document_jeopardy_existant:
                self._client_indexation.supprime_document(
                    identifiant_document_jeopardy_existant
                )

        return resultats


def fabrique_service_indexation_de_documents() -> ServiceIndexationNouveauxDocuments:
    client = fabrique_client_albert()
    configuration = recupere_configuration()
    return ServiceIndexationNouveauxDocuments(
        client,
        configuration.collections_MQC,
        configuration.msc,
        fabrique_service_jeopardise_documents(),
    )
