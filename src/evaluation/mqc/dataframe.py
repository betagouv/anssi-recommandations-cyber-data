import ast
from pathlib import Path
import pandas as pd


def applique_mapping_noms_documents(
    df: pd.DataFrame, chemin_mapping: Path
) -> pd.DataFrame:
    df_resultat = df.copy()
    df_mapping = pd.read_csv(chemin_mapping)

    def _extrait_cinq_premieres_valeurs(liste_noms: list[str]) -> pd.Series:
        resultats = {}
        for i in range(5):
            resultats[f"nom_document_reponse_bot_{i}"] = (
                liste_noms[i] if len(liste_noms) > i else ""
            )
        return pd.Series(resultats)

    def _convertit_liste_str_en_liste(valeur):
        # La valeur est de type str mais contient la représentation d'une liste
        # que l'on souhaite manipuler en tant que tel.
        return ast.literal_eval(valeur)

    def _traite_et_extrait_noms(valeur: str):
        liste_noms = _convertit_liste_str_en_liste(valeur)
        return _extrait_cinq_premieres_valeurs(liste_noms)

    nouvelles_colonnes = df_resultat["Noms Documents"].apply(_traite_et_extrait_noms)
    df_resultat = pd.concat([df_resultat, nouvelles_colonnes], axis=1)

    def obtient_nom_depuis_ref(ref: str) -> str:
        if not isinstance(ref, str) or not ref.strip():
            return ""

        ligne_mapping = df_mapping[df_mapping["REF"] == ref]
        if not ligne_mapping.empty:
            url = ligne_mapping["URL"].iloc[0]
            return url.split("/")[-1]
        return ""

    df_resultat["nom_document_verite_terrain"] = df_resultat["REF Guide"].apply(
        obtient_nom_depuis_ref
    )

    def _extrait_cinq_premiers_numeros_page(liste_pages: list) -> pd.Series:
        resultats = {}
        for i in range(5):
            resultats[f"numero_page_reponse_bot_{i}"] = (
                liste_pages[i] if len(liste_pages) > i else None
            )
        return pd.Series(resultats)

    def _traite_et_extrait_pages(valeur: str):
        liste_pages = _convertit_liste_str_en_liste(valeur)
        return _extrait_cinq_premiers_numeros_page(liste_pages)

    if "Numéros Page" not in df_resultat.columns:
        raise ValueError("La colonne 'Numéros Page' est requise")

    nouvelles_colonnes_pages = df_resultat["Numéros Page"].apply(
        _traite_et_extrait_pages
    )
    df_resultat = pd.concat([df_resultat, nouvelles_colonnes_pages], axis=1)

    if "Numéro page (lecteur)" not in df_resultat.columns:
        raise ValueError("La colonne 'Numéro page (lecteur)' est requise")

    df_resultat["numero_page_verite_terrain"] = df_resultat["Numéro page (lecteur)"]

    return df_resultat


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if "Contexte" in df.columns:
        df["Contexte"] = df["Contexte"].apply(
            lambda x: x.split("${SEPARATEUR_DOCUMENT}")
            if isinstance(x, str) and x.strip()
            else []
        )

    chemin_mapping = Path("donnees/jointure-nom-guide.csv")
    if "Noms Documents" in df.columns and "REF Guide" in df.columns:
        df = applique_mapping_noms_documents(df, chemin_mapping)
    else:
        raise ValueError("Les colonnes 'Noms Documents' et 'REF Guide' sont requises")

    for i in range(5):
        if f"numero_page_reponse_bot_{i}" in df.columns:
            df[f"numero_page_reponse_bot_{i}"] = pd.to_numeric(
                df[f"numero_page_reponse_bot_{i}"], errors="coerce"
            ).fillna(0)

    if "numero_page_verite_terrain" in df.columns:
        df["numero_page_verite_terrain"] = pd.to_numeric(
            df["numero_page_verite_terrain"], errors="coerce"
        ).fillna(0)

    columns_map = {
        "Question type": "query",
        "Réponse Bot": "output",
        "Réponse envisagée": "output_true",
        "Contexte": "context",
    }

    return df.rename(columns=columns_map)
