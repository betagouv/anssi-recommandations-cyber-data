from adaptateurs.clients_albert import ClientAlbertIndexation
from configuration import recupere_configuration, MSC, CollectionsMQC
from documents.indexe_documents_rag import fabrique_client_albert
from documents.pdf.cree_document_pdf import normalise_url
from documents.pdf.document_pdf import DocumentPDFDistant
from jeopardy.service import ServiceJeopardyse, ListeDeDocuments
from jeopardy.service_jeopardyse_liste_de_documents import (
    fabrique_service_jeopardise_documents,
)


class ServiceDIndexation:
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

    def indexe_documents(self, documents: list[str]):
        self._client_indexation.attribue_collection(self._id_collection)
        for document in documents:
            identifiant_document_existant = self._client_indexation.document_existe(
                document
            )
            if identifiant_document_existant:
                self._client_indexation.supprime_document(identifiant_document_existant)
        self._client_indexation.ajoute_documents(
            list(
                map(
                    lambda doc: DocumentPDFDistant(
                        doc, normalise_url(doc, self._configuration_MSC)
                    ),
                    documents,
                )
            )
        )
        self._service_jeopardy.jeopardyse(
            ListeDeDocuments(
                noms_documents=documents,
                id_collection_jeopardy=self._id_collection_jeopardy,
                id_collection_mqc=self._id_collection,
            )
        )


def fabrique_service_indexation_de_documents() -> ServiceDIndexation:
    client = fabrique_client_albert()
    configuration = recupere_configuration()
    return ServiceDIndexation(
        client,
        configuration.collections_MQC,
        configuration.msc,
        fabrique_service_jeopardise_documents(),
    )
