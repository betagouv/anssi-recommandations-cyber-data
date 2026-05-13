from adaptateurs.clients_albert import ClientAlbertIndexation
from configuration import recupere_configuration, MSC
from documents.indexe_documents_rag import fabrique_client_albert
from documents.pdf.cree_document_pdf import normalise_url
from documents.pdf.document_pdf import DocumentPDFDistant


class ServiceDIndexation:
    def __init__(
        self,
        client_indexation: ClientAlbertIndexation,
        id_collection: str,
        configuration_MSC: MSC,
    ):
        super().__init__()
        self.id_collection = id_collection
        self.client_indexation = client_indexation
        self.configuration_MSC = configuration_MSC

    def indexe_documents(self, documents: list[str]):
        self.client_indexation.attribue_collection(self.id_collection)
        self.client_indexation.ajoute_documents(
            list(
                map(
                    lambda doc: DocumentPDFDistant(
                        doc, normalise_url(doc, self.configuration_MSC)
                    ),
                    documents,
                )
            )
        )


def fabrique_service_indexation_de_documents() -> ServiceDIndexation:
    client = fabrique_client_albert()
    configuration = recupere_configuration()
    return ServiceDIndexation(
        client, configuration.collections_MQC.id_collection_indexee, configuration.msc
    )
