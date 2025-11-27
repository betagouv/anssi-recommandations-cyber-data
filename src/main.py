import asyncio
import logging
from pathlib import Path
from adaptateurs.journal import AdaptateurJournal, fabrique_adaptateur_journal
from configuration import recupere_configuration, Configuration
from experience.experience import fabrique_lanceur_experience, LanceurExperience
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
    entrepot_experience: EntrepotExperience,
    journal: AdaptateurJournal,
    lanceur_experience: LanceurExperience,
):
    await collecte_reponses_mqc(
        entree_donnees, prefixe, ecrivain_sortie, nombre_lot, client_mqc
    )
    fichier_csv = ecrivain_sortie._chemin_courant
    if fichier_csv is not None:
        id_experience = lanceur_experience.lance_l_experience(fichier_csv)
        if id_experience is not None:
            consigne_evaluation(
                id_experience, entrepot_experience, journal, fichier_csv
            )
        return id_experience
    return None


if __name__ == "__main__":
    entree = Path("donnees/questions_avec_verite_terrain_3.csv")
    la_configuration: Configuration = recupere_configuration()
    client = ClientMQCHTTPAsync(la_configuration.mqc)
    sortie = Path("/tmp/collecte_reponses")
    sortie.mkdir(parents=True, exist_ok=True)
    ecrivain_sortie = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=sortie, horloge=HorlogeSysteme()
    )
    lanceur_experience = fabrique_lanceur_experience(la_configuration)
    asyncio.run(
        main(
            entree,
            "collecte_reponses_mqc",
            ecrivain_sortie,
            10,
            client,
            fabrique_entrepot_experience(),
            fabrique_adaptateur_journal(),
            lanceur_experience,
        )
    )
