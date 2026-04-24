import argparse
import multiprocessing as mp
from pathlib import Path

from adaptateurs.client_albert_indexation_reel import ClientAlbertIndexationReel
from adaptateurs.clients_albert import ClientAlbertIndexation
from configuration import recupere_configuration, IndexeurDocument
from documents.collecte.collecte import (
    collecte_guides_anssi,
    collecte_documents_distants,
    mappe_en_document_distant,
)
from documents.html.document_html import DocumentReponsesMaitrisees
from documents.indexeur.indexeur import ReponseDocumentEnErreur, ReponseDocumentEnSucces
from documents.indexeur.indexeur_albert import IndexeurBaseVectorielleAlbert
from documents.indexeur.indexeur_docling import IndexeurDocling


def fabrique_client_albert() -> ClientAlbertIndexation:
    config = recupere_configuration().albert
    match config.indexeur:
        case "INDEXEUR_ALBERT":
            return ClientAlbertIndexationReel(
                config.url,
                config.cle_api,
                IndexeurBaseVectorielleAlbert(config.url, 3, 1),
            )
        case "INDEXEUR_DOCLING":
            return ClientAlbertIndexationReel(
                config.url,
                config.cle_api,
                IndexeurDocling(config.url, config.cle_api, config.chunker),  # type: ignore[arg-type]
            )
    raise Exception(
        f"Erreur, un indexeur {', '.join([indexeur.name for indexeur in IndexeurDocument])} doit être fourni. L’indexeur configuré est : {config.indexeur}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nom", required=True, help="Nom de la collection")
    parser.add_argument(
        "--description", required=True, help="Description de la collection"
    )
    parser.add_argument(
        "--documents-distants",
        default="donnees/documents_distants.json",
        help="Fichier json qui spécifie les urls pour les pdf sotckés en dehors de MSS",
    )
    args = parser.parse_args()

    client = fabrique_client_albert()
    client.cree_collection(args.nom, args.description)
    print(f"Collection créée avec ID: {client.id_collection}")
    guides_anssi = collecte_guides_anssi()
    documents_distants = collecte_documents_distants(
        mappe_en_document_distant(Path(args.documents_distants))
    )
    print(
        f"Collecte en cours sur la collection {client.id_collection} :\n"
        f"- Guides ANSSI : {len(guides_anssi)} documents PDF\n"
        f"- Documents distants : {len(documents_distants)} documents"
    )
    reponses = client.ajoute_documents(
        [
            *guides_anssi,
            *documents_distants,
            DocumentReponsesMaitrisees(
                "reponses_maitrisees_ANSSI", "chemin/fichier.html)"
            ),
        ]
    )

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
    mp.set_start_method("spawn", force=True)
    main()
