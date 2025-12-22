import json
import time
from pathlib import Path
import requests

from guides.indexeur import Indexeur, DocumentPDF, PayloadDocument, ReponseDocument


class IndexeurBaseVectorielleAlbert(Indexeur):
    def __init__(self, url: str, max_tentatives: int = 3, temps_d_attente: float = 0.1):
        super().__init__()
        self.url = url
        self.max_tentatives = max_tentatives
        self.temps_d_attente = temps_d_attente
        self.session = requests.session()

    def ajoute_documents(
        self, documents: list[DocumentPDF], id_collection: str | None
    ) -> list[ReponseDocument]:
        reponses = []
        for document in documents:
            reponse_document = self.__ajoute_document_avec_retry(
                document, id_collection
            )
            if reponse_document:
                reponses.append(reponse_document)
        return reponses

    def __ajoute_document(
        self, document: DocumentPDF, id_collection
    ) -> ReponseDocument:
        nom = Path(document.chemin_pdf).name
        with open(document.chemin_pdf, "rb") as flux:
            fichiers = {"file": (nom, flux, "application/pdf")}
            payload = PayloadDocument(
                collection=str(id_collection),
                metadata=json.dumps({"source_url": document.url_pdf}),
                chunk_min_size=150,
            )
            response = self.session.post(
                f"{self.url}/documents", data=payload._asdict(), files=fichiers
            )
        result = response.json()
        print(f"Réponse document API: {result}")
        return ReponseDocument(
            id=result["id"],
            name=result.get("name", nom),
            collection_id=result.get("collection_id", str(id_collection)),
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
        )

    def __ajoute_document_avec_retry(
        self, doc: DocumentPDF, id_collection: str | None
    ) -> ReponseDocument | None:
        succes = False
        tentative = 0
        while tentative < self.max_tentatives and not succes:
            tentative += 1
            try:
                reponse = self.__ajoute_document(doc, id_collection)
                succes = True
                return reponse
            except Exception as e:
                print(f"Tentative {tentative} échouée pour {doc.chemin_pdf}: {e}")
                if tentative < self.max_tentatives:
                    print("Nouvel essai dans 5 secondes...")
                    time.sleep(self.temps_d_attente)
                else:
                    print(
                        f"Échec après {self.max_tentatives} tentatives pour {doc.chemin_pdf}"
                    )
        return None
