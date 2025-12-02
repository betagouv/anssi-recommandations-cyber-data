import glob
from pathlib import Path
from dataclasses import dataclass
import requests
from openai import OpenAI
from configuration import recupere_configuration


@dataclass
class DocumentPDF:
    chemin_pdf: str
    url_pdf: str


class ClientAlbert:
    def __init__(self, url: str, cle_api: str):
        self.client_openai = OpenAI(base_url=url, api_key=cle_api)
        self.session = requests.session()
        self.session.headers = {"Authorization": f"Bearer {cle_api}"}


def fabrique_client_albert() -> ClientAlbert:
    config = recupere_configuration().albert
    return ClientAlbert(config.url, config.cle_api)


def collecte_documents_pdf(
    dossier: str = "donnees/guides_de_lANSSI",
) -> list[DocumentPDF]:
    chemins = glob.glob(f"{dossier}/*.pdf")
    documents = []
    for chemin in chemins:
        nom_fichier = Path(chemin).name
        url = f"https://demo.messervices.cyber.gouv.fr/documents-guides/{nom_fichier}"
        documents.append(DocumentPDF(chemin, url))
    return documents


def main():
    client = fabrique_client_albert()
    documents = collecte_documents_pdf()
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")
    print(f"Collecté {len(documents)} documents PDF")


if __name__ == "__main__":
    main()
