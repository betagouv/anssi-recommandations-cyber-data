import argparse
import asyncio
import logging
from pathlib import Path

from adaptateurs.journal import AdaptateurJournal, fabrique_adaptateur_journal
from configuration import recupere_configuration, Configuration
from evaluation.mqc.collecte_reponses_mqc import collecte_reponses_mqc
from evaluation.mqc.evaluation import LanceurEvaluation
from evaluation.mqc.fabrique_lanceur_evaluation import (
    fabrique_lanceur_evaluation,
)
from evaluation.mqc.remplisseur_reponses import ClientMQCHTTPAsync
from infra.ecrivain_sortie import EcrivainSortie
from infra.horloge import HorlogeSysteme
from journalisation.consignateur_evaluation import consigne_evaluation
from journalisation.evaluation import EntrepotEvaluation, fabrique_entrepot_evaluation

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def evaluateur_mqc(
    entree_donnees: Path,
    prefixe: str,
    ecrivain_sortie: EcrivainSortie,
    nombre_lot: int,
    client_mqc: ClientMQCHTTPAsync,
    entrepot_evaluation: EntrepotEvaluation,
    journal: AdaptateurJournal,
    lanceur_evaluation: LanceurEvaluation,
):
    await collecte_reponses_mqc(
        entree_donnees, prefixe, ecrivain_sortie, nombre_lot, client_mqc
    )
    fichier_csv = ecrivain_sortie._chemin_courant
    if fichier_csv is not None:
        id_evaluation = lanceur_evaluation.lance_l_evaluation(fichier_csv)
        if id_evaluation is not None:
            consigne_evaluation(
                id_evaluation, entrepot_evaluation, journal, fichier_csv
            )
        return id_evaluation
    return None


def parse_arguments(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fichier-evaluation",
        type=Path,
        default=Path("donnees/questions_avec_verite_terrain.csv"),
    )
    parser.add_argument(
        "--fichier-mapping",
        type=Path,
        default=Path("donnees/jointure-nom-guide.csv"),
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_arguments()
    la_configuration: Configuration = recupere_configuration()
    client = ClientMQCHTTPAsync(la_configuration.mqc)
    sortie = Path("/tmp/collecte_reponses")
    sortie.mkdir(parents=True, exist_ok=True)
    ecrivain_sortie = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=sortie, horloge=HorlogeSysteme()
    )
    entrepot_evaluation = fabrique_entrepot_evaluation()
    lanceur_evaluation = fabrique_lanceur_evaluation(
        la_configuration, entrepot_evaluation, chemin_mapping=args.fichier_mapping
    )
    asyncio.run(
        evaluateur_mqc(
            args.fichier_evaluation,
            "collecte_reponses_mqc",
            ecrivain_sortie,
            la_configuration.parametres_deepeval.taille_de_lot_collecte_mqc,
            client,
            entrepot_evaluation,
            fabrique_adaptateur_journal(),
            lanceur_evaluation,
        )
    )
