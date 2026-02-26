import argparse
from typing import Optional

from configuration import MSC, recupere_configuration
from documents.cree_document_pdf import cree_document_pdf
from documents.document_pdf import DocumentPDF
from documents.indexe_documents_rag import (
    fabrique_client_albert,
)
from documents.indexeur import (
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
)


def collecte_document_pdf(
    path: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
    path_url: Optional[str] | None = None,
) -> DocumentPDF:
    return cree_document_pdf(path, configuration_msc, path_url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id_collection", required=True, help="ID de la collection")
    parser.add_argument("--path", required=True, help="Path du document à ajouter")
    parser.add_argument(
        "--guides_urls_externes",
        default="src/guides/guides_urls_externes.json",
        help="Fichier json qui spécifie les urls pour les pdf sotckés en dehors de MSS",
    )

    args = parser.parse_args()

    client = fabrique_client_albert()
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")

    if not client.attribue_collection(args.id_collection):
        print(f"Erreur: Collection avec l'ID {args.id_collection} n'existe pas")
        return

    print(f"Collection trouvée portant l'ID: {client.id_collection}")
    document = collecte_document_pdf(path=args.path, path_url=args.guides_urls_externes)
    reponses = client.ajoute_documents([document])

    les_documents_en_erreur = list(
        filter(lambda reponse: isinstance(reponse, ReponseDocumentEnErreur), reponses)
    )
    les_documents_en_succes = list(
        filter(lambda reponse: isinstance(reponse, ReponseDocumentEnSucces), reponses)
    )

    print(
        f"Ajouté {len(les_documents_en_succes)} documents à la collection {client.id_collection}"
    )
    print(f"{len(les_documents_en_erreur)} documents non ajoutés à la collection :")
    print(
        f"{'-'.join(list(map(lambda document: f'{document.document_en_erreur} - Erreur : {document.detail}', les_documents_en_erreur)))}"
    )


if __name__ == "__main__":
    main()
