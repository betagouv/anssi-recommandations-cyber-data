import asyncio
import logging
import uuid
from pathlib import Path

import requests

from adaptateurs.journal import AdaptateurJournal, fabrique_adaptateur_journal
from configuration import recupere_configuration, Configuration
from evalap import EvalapClient
from evalap.lance_experience import lance_experience
from journalisation.consignateur_evaluation import consigne_evaluation
from journalisation.experience import EntrepotExperience, fabrique_entrepot_experience
from mqc.collecte_reponses_mqc import collecte_reponses_mqc
from mqc.ecrivain_sortie import HorlogeSysteme, EcrivainSortie
from mqc.remplisseur_reponses import ClientMQCHTTPAsync

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def main(
    entree_donnees: Path,
    prefixe: str,
    ecrivain_sortie: EcrivainSortie,
    nombre_lot: int,
    client_mqc: ClientMQCHTTPAsync,
    client_evalap: EvalapClient,
    configuration,
    entrepot_experience: EntrepotExperience,
    journal: AdaptateurJournal,
):
    await collecte_reponses_mqc(
        entree_donnees, prefixe, ecrivain_sortie, nombre_lot, client_mqc
    )
    fichier_csv = ecrivain_sortie._chemin_courant
    nom_evaluation = str(uuid.uuid4())
    id_experience = lance_experience(
        client_evalap, configuration, 10_000, nom_evaluation, fichier_csv
    )
    if id_experience is not None:
        consigne_evaluation(id_experience, entrepot_experience, journal, fichier_csv)
    return id_experience


if __name__ == "__main__":
    entree = Path("donnees/questions_avec_verite_terrain_3.csv")
    la_configuration: Configuration = recupere_configuration()
    client = ClientMQCHTTPAsync(la_configuration.mqc)
    sortie = Path("/tmp/collecte_reponses")
    sortie.mkdir(parents=True, exist_ok=True)
    ecrivain_sortie = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=sortie, horloge=HorlogeSysteme()
    )
    session = requests.session()
    client_evalap = EvalapClient(la_configuration, session)
    asyncio.run(
        main(
            entree,
            "collecte_reponses_mqc",
            ecrivain_sortie,
            10,
            client,
            client_evalap,
            la_configuration,
            fabrique_entrepot_experience(),
            fabrique_adaptateur_journal(),
        )
    )
