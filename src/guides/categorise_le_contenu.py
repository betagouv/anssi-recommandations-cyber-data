import re
from typing import Union

from docling_core.types.doc import (
    TitleItem,
    SectionHeaderItem,
    ListItem,
    CodeItem,
    FormulaItem,
    TextItem,
    TableItem,
)


class Categoriseur:
    def __init__(self, regles_de_categorisation: dict):
        super().__init__()
        self.regles_de_categorisation = regles_de_categorisation

    def prefixe(
        self,
        contenu_courant: Union[
            TitleItem,
            SectionHeaderItem,
            ListItem,
            CodeItem,
            FormulaItem,
            TextItem,
        ],
    ):
        for clef in self.regles_de_categorisation.keys():
            execute_ = self.regles_de_categorisation[clef]["execute"]
            if callable(execute_):
                if execute_(contenu_courant):
                    return self.regles_de_categorisation[clef]["prefixe"]
        return None


class CategorisationTextItem(Categoriseur):
    def __init__(self):
        super().__init__(
            {
                "recommandation": {
                    "execute": lambda contenu_courant: re.match(
                        r"^R\d+$", contenu_courant.text.strip()
                    ),
                    "prefixe": "[RECOMMANDATION]",
                },
                "note": {
                    "execute": lambda contenu_courant: hasattr(contenu_courant, "label")
                    and str(contenu_courant.label) == "footnote",
                    "prefixe": "[NOTE]",
                },
                "texte": {
                    "execute": lambda contenu_courant: True,
                    "prefixe": "[TEXTE]",
                },
            }
        )


class CategorisationSectionHeaderItem(Categoriseur):
    def __init__(self):
        super().__init__(
            {
                "recommandation": {
                    "execute": lambda contenu_courant: re.match(
                        r"^R\d+$", contenu_courant.text.strip()
                    ),
                    "prefixe": "[RECOMMANDATION]",
                },
                "note": {
                    "execute": lambda contenu_courant: re.match(
                        r"^\d+\.\d+", contenu_courant.text.strip()
                    ),
                    "prefixe": "[SECTION]",
                },
                "texte": {
                    "execute": lambda contenu_courant: True,
                    "prefixe": "[SOUS-TITRE]",
                },
            }
        )


class CategorisationTableItem(Categoriseur):
    def __init__(self):
        super().__init__({})

    def prefixe(
        self,
        contenu_courant: Union[
            TitleItem,
            SectionHeaderItem,
            ListItem,
            CodeItem,
            FormulaItem,
            TextItem,
            TableItem,
        ],
    ):
        prefix = "[TABLEAU]\n"
        table_text = ""
        if hasattr(contenu_courant, "data") and contenu_courant.data:
            for row in contenu_courant.data.grid:
                row_text = " | ".join(cell.text for cell in row)
                table_text += f"| {row_text} |\n"
                est_ligne_entete = all(map(lambda cell: cell.column_header, row))
                if est_ligne_entete:
                    row_entete = " | ".join("---" for cell in row)
                    table_text += f"| {row_entete} |\n"
        return f"{prefix}{table_text.strip()}"


def ajoute_la_categorisation_du_contenu(
    contenu_courant: Union[
        TitleItem,
        SectionHeaderItem,
        ListItem,
        CodeItem,
        FormulaItem,
        TextItem,
        TableItem,
    ],
) -> str:
    current_type = type(contenu_courant).__name__
    if isinstance(contenu_courant, SectionHeaderItem):
        return f"{CategorisationSectionHeaderItem().prefixe(contenu_courant)} {contenu_courant.text}"
    elif isinstance(contenu_courant, TextItem):
        return f"{CategorisationTextItem().prefixe(contenu_courant)} {contenu_courant.text}"
    elif isinstance(contenu_courant, TableItem):
        return CategorisationTableItem().prefixe(contenu_courant)
    else:
        return f"[{current_type.upper()}] {contenu_courant.text}"
