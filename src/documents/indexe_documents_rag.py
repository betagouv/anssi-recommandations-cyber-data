import argparse
import glob
import multiprocessing as mp

from adaptateurs.client_albert import ClientAlbert
from adaptateurs.client_albert_reel import ClientAlbertReel
from configuration import recupere_configuration, IndexeurDocument, MSC
from documents.indexeur import (
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
)
from documents.indexeur_albert import IndexeurBaseVectorielleAlbert
from documents.indexeur_docling import IndexeurDocling
from documents.pdf.cree_document_pdf import cree_document_pdf
from documents.pdf.document_pdf import DocumentPDF


def fabrique_client_albert() -> ClientAlbert:
    config = recupere_configuration().albert
    match config.indexeur:
        case "INDEXEUR_ALBERT":
            return ClientAlbertReel(
                config.url,
                config.cle_api,
                IndexeurBaseVectorielleAlbert(config.url, 3, 1),
            )
        case "INDEXEUR_DOCLING":
            return ClientAlbertReel(
                config.url,
                config.cle_api,
                IndexeurDocling(config.url, config.cle_api, config.chunker),  # type: ignore[arg-type]
            )
    raise Exception(
        f"Erreur, un indexeur {', '.join([indexeur.name for indexeur in IndexeurDocument])} doit être fourni. L’indexeur configuré est : {config.indexeur}"
    )


def collecte_guides_anssi(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> list[DocumentPDF]:
    chemins = glob.glob(f"{dossier}/*.pdf")
    return [cree_document_pdf(chemin, configuration_msc) for chemin in chemins]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nom", required=True, help="Nom de la collection")
    parser.add_argument(
        "--description", required=True, help="Description de la collection"
    )
    parser.add_argument(
        "--documents-distants",
        default="src/guides/documents_distants.json",
        help="Fichier json qui spécifie les urls pour les pdf sotckés en dehors de MSS",
    )
    args = parser.parse_args()

    client = fabrique_client_albert()
    print(f"Client Albert créé avec URL: {client.client_openai.base_url}")

    client.cree_collection(args.nom, args.description)
    print(f"Collection créée avec ID: {client.id_collection}")
    documents = collecte_guides_anssi()
    print(
        f"Collecté {len(documents)} documents PDF sur la collection {client.id_collection}"
    )
    reponses = client.ajoute_documents(documents)

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
