import argparse
import glob
from pathlib import Path
import requests
from openai import OpenAI
from typing_extensions import NamedTuple
from configuration import recupere_configuration, MSC
from guides.indexeur import DocumentPDF, ReponseDocument
from guides.indexeur_albert import IndexeurBaseVectorielleAlbert


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
        if response.status_code != 201:
            print(f"Erreur {response.status_code}: {response.text}")
            raise Exception(f"Erreur création collection: {response.status_code}")
        result = response.json()
        print(f"Réponse API: {result}")
        self.id_collection = result["id"]
        return ReponseCollection(
            id=result["id"],
            name=result.get("name", nom),
            description=result.get("description", description),
            visibility=result.get("visibility", "private"),
            documents=result.get("documents", 0),
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
        )

    def ajoute_documents(
        self,
        documents: list[DocumentPDF],
        max_tentatives: int = 3,
        temps_d_attente: float = 0.1,
    ) -> list[ReponseDocument]:
        id_collection = self.id_collection
        url = self.url
        return IndexeurBaseVectorielleAlbert(
            url, max_tentatives, temps_d_attente
        ).ajoute_documents(documents, id_collection)


def fabrique_client_albert() -> ClientAlbert:
    config = recupere_configuration().albert
    return ClientAlbert(config.url, config.cle_api)


def collecte_documents_pdf(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> list[DocumentPDF]:
    chemins = glob.glob(f"{dossier}/*.pdf")
    documents = []
    for chemin in chemins:
        nom_fichier = Path(chemin).name
        url = f"{configuration_msc.url}/{configuration_msc.chemin_guides}/{nom_fichier}"
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
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")

    client.cree_collection(args.nom, args.description)
    print(f"Collection créée avec ID: {client.id_collection}")
    documents = collecte_documents_pdf()
    print(f"Collecté {len(documents)} documents PDF")
    reponses = client.ajoute_documents(documents, 3, 1)
    print(f"Ajouté {len(reponses)} documents à la collection")


if __name__ == "__main__":
    main()
