from pathlib import Path
from typing import Mapping, Union
import pytest

from infra.lecteur_csv import LecteurCSV


def test_peut_lire_un_fichier_csv_et_compter_les_lignes(tmp_path: Path):
    fichier = tmp_path / "exemple.csv"
    contenu = "col1,col2\nval1,val2\nval3,val4\n"
    fichier.write_text(contenu, encoding="utf-8")

    lecteur = LecteurCSV(fichier)
    lignes = list(lecteur.iterer_lignes())

    assert len(lignes) == 2
    assert lignes[0]["col1"] == "val1"
    assert lignes[1]["col2"] == "val4"


def test_peut_inserer_dans_une_colonne_en_utilisant_une_fonction_transmise(
    tmp_path: Path,
):
    fichier = tmp_path / "ex.csv"
    fichier.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    lecteur = LecteurCSV(fichier)

    ligne1 = lecteur.ligne_suivante()
    ligne1_enrichie = lecteur.appliquer_calcul_ligne(
        "somme", lambda d: int(d["a"]) + int(d["b"]), ligne1
    )

    ligne2 = lecteur.ligne_suivante()
    ligne2_enrichie = lecteur.appliquer_calcul_ligne(
        "somme", lambda d: int(d["a"]) + int(d["b"]), ligne2
    )

    assert ligne1_enrichie["somme"] == 3
    assert ligne2_enrichie["somme"] == 7


def test_peut_ecrire_un_csv(tmp_path: Path):
    fichier = tmp_path / "ex.csv"
    fichier.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    lecteur = LecteurCSV(fichier)

    sortie = tmp_path / "out.csv"
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("a,b,somme\n")

        ligne1 = lecteur.ligne_suivante()
        ligne1_enrichie = lecteur.appliquer_calcul_ligne(
            "somme", lambda d: int(d["a"]) + int(d["b"]), ligne1
        )
        f.write(
            f"{ligne1_enrichie['a']},{ligne1_enrichie['b']},{ligne1_enrichie['somme']}\n"
        )

        ligne2 = lecteur.ligne_suivante()
        ligne2_enrichie = lecteur.appliquer_calcul_ligne(
            "somme", lambda d: int(d["a"]) + int(d["b"]), ligne2
        )
        f.write(
            f"{ligne2_enrichie['a']},{ligne2_enrichie['b']},{ligne2_enrichie['somme']}\n"
        )

    contenu = sortie.read_text(encoding="utf-8").strip().splitlines()
    assert contenu[0] == "a,b,somme"
    assert "1,2,3" in contenu[1]
    assert "3,4,7" in contenu[2]


def test_iterer_lignes_retourne_un_iterateur_de_dict(tmp_path: Path):
    fichier = tmp_path / "ex.csv"
    fichier.write_text("a,b,texte\n1,2,x\n3,4,y\n", encoding="utf-8")

    lecteur = LecteurCSV(fichier)
    it = lecteur.iterer_lignes()

    ligne1 = next(it)
    assert isinstance(ligne1, dict)
    assert ligne1["a"] == 1
    assert ligne1["b"] == 2
    assert ligne1["texte"] == "x"

    ligne2 = next(it)
    assert ligne2 == {"a": 3, "b": 4, "texte": "y"}

    try:
        next(it)
        assert False, "L'itérateur devrait être vide"
    except StopIteration:
        pass


def test_iterer_lignes_sur_csv_sans_donnees_retourne_vide(tmp_path: Path):
    fichier = tmp_path / "vide.csv"
    fichier.write_text("col1,col2\n", encoding="utf-8")  # seulement l’en-tête

    lecteur = LecteurCSV(fichier)
    lignes = list(lecteur.iterer_lignes())
    assert lignes == []


def test_lecteur_appliquer_calcul_ligne_enrichit_une_ligne(tmp_path: Path):
    """Test que le lecteur peut appliquer un calcul sur une ligne spécifique"""
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type,autre\nQ1?,valeur\n", encoding="utf-8")

    lecteur = LecteurCSV(fichier)

    def calcul_test(ligne: Mapping[str, Union[str, int, float]]) -> str:
        return f"calculé_{ligne['Question type']}"

    ligne_originale = {"Question type": "Q1?", "autre": "valeur"}

    ligne_enrichie = lecteur.appliquer_calcul_ligne(
        "Nouvelle Colonne", calcul_test, ligne_originale
    )

    assert ligne_enrichie["Question type"] == "Q1?"
    assert ligne_enrichie["autre"] == "valeur"
    assert ligne_enrichie["Nouvelle Colonne"] == "calculé_Q1?"


@pytest.mark.parametrize(
    "nb_lignes_header,contenu_header",
    [
        (0, ""),
        (1, "# Une ligne de header\n"),
        (2, "# Première ligne\n# Deuxième ligne\n"),
        (
            3,
            "# AVERTISSEMENT: Ce jeu de données est en cours de construction\n# Il ne doit pas engager l'ANSSI\n# \n",
        ),
    ],
)
def test_lecture_csv_avec_header_avertissement(
    tmp_path, nb_lignes_header, contenu_header
):
    contenu_csv = contenu_header + "nom,age,ville\nAlice,25,Paris\nBob,30,Lyon"
    fichier_test = tmp_path / "test_avec_header.csv"
    fichier_test.write_text(contenu_csv, encoding="utf-8")

    lecteur = LecteurCSV(fichier_test)
    df = lecteur.dataframe

    assert len(df) == 2
    assert list(df.columns) == ["nom", "age", "ville"]
    assert df.iloc[0]["nom"] == "Alice"
    assert df.iloc[1]["nom"] == "Bob"


def test_lecture_fichier_questions_avec_verite_terrain():
    chemin_fichier = Path("donnees/questions_avec_verite_terrain.csv")
    lecteur = LecteurCSV(chemin_fichier)
    df = lecteur.dataframe
    assert len(df) > 0
    assert "REF Guide" in df.columns
    assert "Question type" in df.columns
    premiere_ligne = next(lecteur.iterer_lignes())
    assert "REF Guide" in premiere_ligne
