import argparse
import glob
import json
import time
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


class PayloadDocument(NamedTuple):
    collection: str
    metadata: str


class ReponseCollection(NamedTuple):
    id: str
    name: str
    description: str
    visibility: str
    documents: int
    created_at: str
    updated_at: str


class ReponseDocument(NamedTuple):
    id: str
    name: str
    collection_id: str
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

    def ajoute_document(self, document: DocumentPDF) -> list[ReponseDocument]:
        reponses = []
        nom = Path(document.chemin_pdf).name
        with open(document.chemin_pdf, "rb") as flux:
            fichiers = {"file": (nom, flux, "application/pdf")}
            payload = PayloadDocument(
                collection=str(self.id_collection),
                metadata=json.dumps({"source_url": document.url_pdf}),
            )
            response = self.session.post(
                f"{self.url}/documents", data=payload._asdict(), files=fichiers
            )
        result = response.json()
        print(f"Réponse document API: {result}")
        reponses.append(
            ReponseDocument(
                id=result["id"],
                name=result.get("name", nom),
                collection_id=result.get("collection_id", str(self.id_collection)),
                created_at=result.get("created_at", ""),
                updated_at=result.get("updated_at", ""),
            )
        )
        return reponses

    def ajoute_documents_avec_retry(
        self,
        documents: list[DocumentPDF],
        max_tentatives: int = 3,
        temps_d_attente: float = 0.1,
    ) -> list[ReponseDocument]:
        reponses = []
        for doc in documents:
            succes = False
            tentative = 0

            while tentative < max_tentatives and not succes:
                tentative += 1
                try:
                    reponse = self.ajoute_document(doc)
                    reponses.extend(reponse)
                    succes = True
                except Exception as e:
                    print(f"Tentative {tentative} échouée pour {doc.chemin_pdf}: {e}")
                    if tentative < max_tentatives:
                        print("Nouvel essai dans 5 secondes...")
                        time.sleep(temps_d_attente)
                    else:
                        print(
                            f"Échec après {max_tentatives} tentatives pour {doc.chemin_pdf}"
                        )
        return reponses


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
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")

    client.cree_collection(args.nom, args.description)
    print(f"Collection créée avec ID: {client.id_collection}")
    documents = collecte_documents_pdf()
    print(f"Collecté {len(documents)} documents PDF")
    reponses = client.ajoute_documents_avec_retry(documents, 3, 1)
    print(f"Ajouté {len(reponses)} documents à la collection")


if __name__ == "__main__":
    main()
