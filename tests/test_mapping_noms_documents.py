import pandas as pd
import pytest
from pathlib import Path
from main_evalap import applique_mapping_noms_documents, prepare_dataframe


def test_applique_mapping_noms_documents_avec_ref_valide(tmp_path: Path):
    mapping_csv = tmp_path / "mapping.csv"
    mapping_csv.write_text(
        "REF,Nom,URL\nGAUT,Guide Authentification,https://example.com/guide-auth.pdf\nGCRI,Guide Crise,https://example.com/guide-crise.pdf\n",
        encoding="utf-8",
    )

    df = pd.DataFrame(
        {
            "Noms Documents": ["['Doc1', 'Doc2']", "['Doc3']"],
            "REF Guide": ["GAUT", "GCRI"],
            "Numéros Page": ["[1, 2]", "[3]"],
            "Numéro page (lecteur)": [1, 3],
        }
    )

    df_resultat = applique_mapping_noms_documents(df, mapping_csv)

    for i in range(5):
        assert f"nom_document_reponse_bot_{i}" in df_resultat.columns
    assert "nom_document_verite_terrain" in df_resultat.columns
    assert df_resultat["nom_document_verite_terrain"].iloc[0] == "guide-auth.pdf"
    assert df_resultat["nom_document_verite_terrain"].iloc[1] == "guide-crise.pdf"

    assert df_resultat["nom_document_reponse_bot_0"].iloc[0] == "Doc1"
    assert df_resultat["nom_document_reponse_bot_0"].iloc[1] == "Doc3"

    assert df_resultat["nom_document_reponse_bot_1"].iloc[0] == "Doc2"


def test_applique_mapping_noms_documents_avec_liste_vide():
    df = pd.DataFrame(
        {
            "Noms Documents": ["[]"],
            "REF Guide": ["GAUT"],
            "Numéros Page": ["[]"],
            "Numéro page (lecteur)": [1],
        }
    )

    mapping_csv = Path("./donnees/jointure-nom-guide.csv")
    df_resultat = applique_mapping_noms_documents(df, mapping_csv)

    assert df_resultat["nom_document_reponse_bot_0"].iloc[0] == ""


def test_applique_mapping_noms_documents_avec_ref_inexistante():
    df = pd.DataFrame(
        {
            "Noms Documents": ["['Doc1']"],
            "REF Guide": ["INEXISTANT"],
            "Numéros Page": ["[5]"],
            "Numéro page (lecteur)": [5],
        }
    )

    mapping_csv = Path("./donnees/jointure-nom-guide.csv")
    df_resultat = applique_mapping_noms_documents(df, mapping_csv)

    assert df_resultat["nom_document_verite_terrain"].iloc[0] == ""


@pytest.mark.parametrize(
    "colonnes_df",
    [
        {"REF Guide": ["GAUT"]},
        {"Noms Documents": [["Doc1"]]},
        {"Autre Colonne": [["Autre"]]},
    ],
)
def test_prepare_dataframe_leve_erreur_si_colonnes_manquantes(colonnes_df):
    df = pd.DataFrame(colonnes_df)

    with pytest.raises(
        ValueError, match="Les colonnes 'Noms Documents' et 'REF Guide' sont requises"
    ):
        prepare_dataframe(df)


def test_applique_mapping_leve_erreur_si_colonne_numeros_page_manquant():
    df = pd.DataFrame(
        {
            "Noms Documents": ["['Doc1']"],
            "REF Guide": ["GAUT"],
            # Pas de colonne "Numéros Page"
        }
    )

    mapping_csv = Path("./donnees/jointure-nom-guide.csv")

    with pytest.raises(ValueError, match="La colonne 'Numéros Page' est requise"):
        applique_mapping_noms_documents(df, mapping_csv)
