from documents.elements_filtres import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.page import Page


class Document:
    def __init__(self, nom_document, url):
        super().__init__()
        self._nom_document = nom_document
        self._url = url
        self.pages: dict[int, Page] = {}

    @property
    def nom_document(self):
        return self._nom_document

    @property
    def url(self):
        return self._url

    def metadata(self, page) -> dict:
        return {
            "source_url": self.url,
            "page": page.numero_page if page.numero_page is not None else 0,
            "nom_document": self.nom_document,
        }

    def genere_les_pages(
        self, generateur: GenerateurDePages, elements_filtres: ElementsFiltres
    ):
        self.pages = generateur.genere(elements_filtres)
