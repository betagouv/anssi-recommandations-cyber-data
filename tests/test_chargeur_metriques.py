import pytest
from pathlib import Path
from src.chargeur_metriques import ChargeurMetriques, MetriqueEnum


def test_charge_metriques_depuis_fichier_valide(tmp_path):
    fichier_config = tmp_path / "metriques.json"
    fichier_config.write_text('{"metriques": ["judge_precision", "toxicity"]}')

    chargeur = ChargeurMetriques()
    metriques = chargeur.charge_depuis_fichier(fichier_config)

    assert metriques == [MetriqueEnum.JUDGE_PRECISION, MetriqueEnum.TOXICITY]


def test_charge_metriques_fichier_inexistant():
    chargeur = ChargeurMetriques()

    with pytest.raises(FileNotFoundError):
        chargeur.charge_depuis_fichier(Path("inexistant.json"))


def test_charge_metriques_invalides(tmp_path):
    fichier_config = tmp_path / "metriques.json"
    fichier_config.write_text('{"metriques": ["metrique_inexistante"]}')

    chargeur = ChargeurMetriques()

    with pytest.raises(ValueError):
        chargeur.charge_depuis_fichier(fichier_config)
