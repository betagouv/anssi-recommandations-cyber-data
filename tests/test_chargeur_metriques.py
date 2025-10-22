import pytest
from pathlib import Path
from metriques import Metriques, MetriqueEnum


def test_charge_metriques_depuis_fichier_valide(tmp_path):
    fichier_config = tmp_path / "metriques.json"
    fichier_config.write_text('{"metriques": ["judge_precision", "toxicity"]}')

    chargeur = Metriques()
    metriques = chargeur.recupere_depuis_fichier(fichier_config)

    assert metriques == [MetriqueEnum.JUDGE_PRECISION, MetriqueEnum.TOXICITY]


def test_charge_metriques_fichier_inexistant():
    chargeur = Metriques()

    with pytest.raises(FileNotFoundError):
        chargeur.recupere_depuis_fichier(Path("inexistant.json"))


def test_charge_metriques_invalides(tmp_path):
    fichier_config = tmp_path / "metriques.json"
    fichier_config.write_text('{"metriques": ["metrique_inexistante"]}')

    chargeur = Metriques()

    with pytest.raises(
        ValueError, match="'metrique_inexistante' is not a valid MetriqueEnum"
    ):
        chargeur.recupere_depuis_fichier(fichier_config)
