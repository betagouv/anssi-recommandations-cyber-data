import asyncio
import logging
from pathlib import Path
from configuration import recupere_configuration
from mqc.collecte_reponses_mqc import collecte_reponses_mqc
from mqc.remplisseur_reponses import ClientMQCHTTPAsync

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def main(
    entree_donnees: Path,
    sortie_collecte: Path,
    prefixe: str,
    nombre_lot: int,
    client_mqc: ClientMQCHTTPAsync,
):
    await collecte_reponses_mqc(
        entree_donnees, sortie_collecte, prefixe, nombre_lot, client_mqc
    )


if __name__ == "__main__":
    entree = Path("donnees/questions_avec_verite_terrain_3.csv")
    configuration_mqc = recupere_configuration().mqc
    client = ClientMQCHTTPAsync(configuration_mqc)
    sortie = Path("/tmp/collecte_reponses")
    sortie.mkdir(parents=True, exist_ok=True)
    asyncio.run(main(entree, sortie, "collecte_reponses_mqc", 10, client))
