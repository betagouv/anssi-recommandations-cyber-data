import logging
import re
from typing import Union

import regex
from docling.document_converter import ConversionResult
from docling_core.types.doc import (
    TitleItem,
    SectionHeaderItem,
    ListItem,
    CodeItem,
    FormulaItem,
    TextItem,
    TableItem,
)


def filtre_les_resultats(
    result: ConversionResult,
) -> list[
    Union[
        TitleItem,
        SectionHeaderItem,
        ListItem,
        CodeItem,
        FormulaItem,
        TextItem,
        TableItem,
    ]
]:
    elements_filtres: list[
        Union[
            TitleItem,
            SectionHeaderItem,
            ListItem,
            CodeItem,
            FormulaItem,
            TextItem,
            TableItem,
        ]
    ] = []
    for text_item in result.document.texts:
        if _est_un_texte_utile(text_item.text):
            elements_filtres.append(text_item)

    for table_item in result.document.tables:
        elements_filtres.append(table_item)
    return elements_filtres


def _est_un_texte_utile(texte: str) -> bool:
    try:
        if not texte:
            return False
        t = texte.strip()
        if not t:
            return False

        matche_recommandation = re.match(r"^[R]\d+$", t)
        if matche_recommandation:
            return True
        les_characteres_latin_etendu = regex.findall(r"[\p{Latin}']+", texte)
        nombre_de_mots = len(les_characteres_latin_etendu)
        nombre_de_lettres = sum(c.isalpha() for c in t)
        ratio_nombre_de_lettre_sur_longueur_de_chaine = nombre_de_lettres / max(
            len(t), 1
        )
        if nombre_de_mots >= 1 and ratio_nombre_de_lettre_sur_longueur_de_chaine >= 0.6:
            return True

        return False
    except Exception as exc:
        logging.debug("Erreur _est_lisible: %s", exc)
        return False
