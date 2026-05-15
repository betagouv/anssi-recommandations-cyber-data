from adaptateurs.clients_albert import ClientAlbertIndexation
from configuration import MSC
from documents.pdf.cree_document_pdf import normalise_url
from documents.pdf.document_pdf import DocumentPDFDistant
from jeopardy.service import ServiceJeopardyse


class ServiceIndexationNouvellesCollections:
    def __init__(
        self,
        client_indexation: ClientAlbertIndexation,
        configuration_MSC: MSC,
        service_jeopardy: ServiceJeopardyse,
    ):
        super().__init__()
        self._service_jeopardy = service_jeopardy
        self._client_indexation = client_indexation
        self._configuration_MSC = configuration_MSC

    def indexe_documents(self, nom: str, description: str, documents: list[str]):
        reponse_collection = self._client_indexation.cree_collection(nom, description)
        self._client_indexation.attribue_collection(reponse_collection.id)
        resultats = self._client_indexation.ajoute_documents(
            list(
                map(
                    lambda doc: DocumentPDFDistant(
                        doc, normalise_url(doc, self._configuration_MSC)
                    ),
                    documents,
                )
            )
        )
        return resultats
