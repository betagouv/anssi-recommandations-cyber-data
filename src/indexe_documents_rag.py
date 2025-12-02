import argparse
import glob
from pathlib import Path
from dataclasses import dataclass
from typing_extensions import NamedTuple
import requests
from openai import OpenAI
from configuration import recupere_configuration


@dataclass
class DocumentPDF:
    chemin_pdf: str
    url_pdf: str


class PayloadCollection(NamedTuple):
    name: str
    description: str
    visibility: str = "private"


class ReponseCollection(NamedTuple):
    id: str
    name: str
    description: str
    visibility: str
    documents: int
    created_at: str
    updated_at: str


class ClientAlbert:
    def __init__(self, url: str, cle_api: str):
        self.url = url
        self.client_openai = OpenAI(base_url=url, api_key=cle_api)
        self.session = requests.session()
        self.session.headers = {"Authorization": f"Bearer {cle_api}"}
        self.id_collection: str | None = None

    def cree_collection(self, nom: str, description: str) -> ReponseCollection:
        payload = PayloadCollection(name=nom, description=description)
        response = self.session.post(f"{self.url}/collections", json=payload._asdict())
        result = response.json()
        reponse_collection = ReponseCollection(**result)
        self.id_collection = reponse_collection.id
        return reponse_collection


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--nom", required=True, help="Nom de la collection")
    parser.add_argument(
        "--description", required=True, help="Description de la collection"
    )
    args = parser.parse_args()

    client = fabrique_client_albert()
    client.cree_collection(args.nom, args.description)
    documents = collecte_documents_pdf()

    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")
    print(f"Collection créée avec ID: {client.id_collection}")
    print(f"Collecté {len(documents)} documents PDF")


if __name__ == "__main__":
    main()
