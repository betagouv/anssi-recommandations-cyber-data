from pathlib import Path
from mqc.remplisseur_reponses import ClientMQCHTTPAsync
from mqc.traite_csv_par_lots_en_parallele import traite_csv_par_lots_en_parallele


async def collecte_reponses_mqc(
    chemin_csv: Path,
    chemin_sortie: Path,
    prefixe: str,
    taille_lot: int,
    client: ClientMQCHTTPAsync,
) -> None:
    await traite_csv_par_lots_en_parallele(
        csv_path=chemin_csv,
        prefixe=prefixe,
        sortie=Path(chemin_sortie),
        taille_lot=taille_lot,
        client=client,
    )

    return None
