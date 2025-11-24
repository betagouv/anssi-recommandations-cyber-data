import glob
from pathlib import Path
import httpx
import pytest
import respx
from configuration import Configuration
from main import main
from mqc.remplisseur_reponses import (
    ClientMQCHTTPAsync,
    construit_base_url,
    formate_route_pose_question,
)


@respx.mock
@pytest.mark.asyncio
async def test_execute_la_collecte_des_reponses_pour_creer_le_fichier_de_resultat_de_collecte(
    tmp_path: Path,
    configuration: Configuration,
    fichier_evaluation,
    reponse_avec_paragraphes,
):
    base = construit_base_url(configuration.mqc)
    chemin = formate_route_pose_question(configuration.mqc)
    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )

    entree = fichier_evaluation("Question type\nA?\n", tmp_path)
    sortie = tmp_path.joinpath("sortie")
    await main(entree, sortie, "prefixe", 1, ClientMQCHTTPAsync(cfg=configuration.mqc))

    assert sortie.exists()
    collectes = glob.glob(str(sortie) + "/*")
    assert Path(collectes[0]).name.startswith("prefixe_") is True
