from pathlib import Path
from lecteur_csv import LecteurCSV


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
    lecteur.appliquer_calcul_colonne("somme", lambda d: int(d["a"]) + int(d["b"]))

    df = lecteur.dataframe
    assert list(df["somme"]) == [3, 7]


def test_peut_ecrire_un_csv(tmp_path: Path):
    fichier = tmp_path / "ex.csv"
    fichier.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    lecteur = LecteurCSV(fichier)
    lecteur.appliquer_calcul_colonne("somme", lambda d: int(d["a"]) + int(d["b"]))

    sortie = tmp_path / "out.csv"
    lecteur.ecrire_vers(sortie)
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
