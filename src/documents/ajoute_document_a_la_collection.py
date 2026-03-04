import argparse
from pathlib import Path

from documents.collecte.collecte import (
    collecte_guide_anssi,
    collecte_documents_distants,
    mappe_en_document_distant,
)
from documents.indexe_documents_rag import (
    fabrique_client_albert,
)
from documents.indexeur import (
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id_collection", required=True, help="ID de la collection")
    parser.add_argument("--path", required=True, help="Path du document à ajouter")
    parser.add_argument(
        "--documents-distants",
        default="src/guides/documents_distants.json",
        help="Fichier json qui spécifie les urls pour les pdf sotckés en dehors de MSS",
    )

    args = parser.parse_args()

    client = fabrique_client_albert()
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")

    if not client.attribue_collection(args.id_collection):
        print(f"Erreur: Collection avec l'ID {args.id_collection} n'existe pas")
        return

    print(f"Collection trouvée portant l'ID: {client.id_collection}")
    guides_anssi = collecte_guide_anssi(path=args.path)
    documents_distants = collecte_documents_distants(
        mappe_en_document_distant(Path(args.documents_distants))
    )
    reponses = client.ajoute_documents([guides_anssi, *documents_distants])

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
