import argparse
import glob
import multiprocessing as mp
from pathlib import Path
from urllib.parse import quote

import unicodedata

from adaptateurs.client_albert import ClientAlbert
from adaptateurs.client_albert_reel import ClientAlbertReel
from configuration import recupere_configuration, IndexeurDocument, MSC
from guides.indexeur import (
    DocumentPDF,
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
)
from guides.indexeur_albert import IndexeurBaseVectorielleAlbert
from guides.indexeur_docling import IndexeurDocling


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


def _cree_document_pdf(chemin: str, configuration_msc: MSC) -> DocumentPDF:
    base = configuration_msc.url.rstrip("/")
    chemin_guides = configuration_msc.chemin_guides.strip("/")
    nom_fichier = Path(chemin).name
    nom_fichier = unicodedata.normalize("NFC", nom_fichier)
    nom_fichier_encode = quote(nom_fichier, safe="-._~")
    url = f"{base}/{chemin_guides}/{nom_fichier_encode}"
    return DocumentPDF(chemin, url)


def collecte_documents_pdf(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> list[DocumentPDF]:
    chemins = glob.glob(f"{dossier}/*.pdf")
    return [_cree_document_pdf(chemin, configuration_msc) for chemin in chemins]


def collecte_document_pdf(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> DocumentPDF:
    chemins = glob.glob(f"{dossier}/*.pdf")
    return _cree_document_pdf(chemins[0], configuration_msc)


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
