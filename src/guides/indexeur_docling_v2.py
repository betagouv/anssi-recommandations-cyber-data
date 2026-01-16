import argparse
import logging
import sys
from pathlib import Path

from guides.chunker_docling_mqc import ChunkerDoclingMQC
from guides.guide import Guide

sys.path.append("src")
from guides.indexeur_docling import DocumentPDF

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def affiche_le_guide(guide, nom_document: str):
    for page in guide.pages.values():
        print(f"Document : {nom_document}")
        print(f"Blocs    : {len(page.blocs)}")
        for i, bloc in enumerate(page.blocs):
            print(f"\n[Bloc {i}]")
            print(bloc.texte)
            print("\n-------------------------------")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chunker Docling v2 avec fusion entête/paragraphe"
    )
    parser.add_argument("--pdf", required=True, help="Chemin vers le fichier PDF")
    parser.add_argument("--log-file", help="Fichier de log (optionnel)")
    parser.add_argument("--debug", action="store_true", help="Active les logs DEBUG")
    parser.add_argument(
        "--taille-maximale",
        type=int,
        default=1000,
        help="Taille maximale d'un bloc fusionné (défaut: 1000)",
    )

    args = parser.parse_args()

    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    if args.log_file:
        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO,
            format=log_format,
            filename=args.log_file,
            filemode="w",
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG if args.debug else logging.INFO, format=log_format
        )

    try:
        logging.info("Initialisation du chunker Docling v2...")
        chunker = ChunkerDoclingMQC()

        document = DocumentPDF(chemin_pdf=args.pdf, url_pdf="")

        logging.info("Extraction des chunks avec fusion...")
        guide: Guide = chunker.applique(document)

        logging.info("Nombre de chunks extraits: %d", len(guide.pages))

        if not guide:
            logging.warning("Aucun chunk extrait du PDF")
            return 0

        # pages_avec_fusion: dict[int, list[BlocPage]] = (
        #     chunker.fusionne_les_blocs_de_la_meme_page(chunks, args.taille_maximale)
        # )
        #
        affiche_le_guide(guide, Path(args.pdf).name)

        logging.info("Traitement terminé avec succès")
        return 0

    except Exception as exc:
        logging.error("Erreur: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
