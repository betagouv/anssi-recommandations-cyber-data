import argparse
import glob

from configuration import MSC, recupere_configuration
from guides.cree_document_pdf import cree_document_pdf
from guides.indexe_documents_rag import (
    fabrique_client_albert,
)
from guides.indexeur import (
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
    DocumentPDF,
)


def collecte_document_pdf(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> DocumentPDF:
    chemins = glob.glob(f"{dossier}/*.pdf")
    return cree_document_pdf(chemins[0], configuration_msc)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id_collection", required=True, help="ID de la collection")
    parser.add_argument("--path", required=True, help="Path du document à ajouter")
    args = parser.parse_args()

    client = fabrique_client_albert()
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")

    if not client.attribue_collection(args.id_collection):
        print(f"Erreur: Collection avec l'ID {args.id_collection} n'existe pas")
        return

    print(f"Collection trouvée portant l'ID: {client.id_collection}")
    document = collecte_document_pdf(path=args.path)
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
