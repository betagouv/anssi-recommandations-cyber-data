from docling_core.types.doc import (
    TitleItem,
    SectionHeaderItem,
    ListItem,
    CodeItem,
    FormulaItem,
    TextItem,
    TableItem,
)

type ElementsFiltres = list[
    TitleItem
    | SectionHeaderItem
    | ListItem
    | CodeItem
    | FormulaItem
    | TextItem
    | TableItem
]
