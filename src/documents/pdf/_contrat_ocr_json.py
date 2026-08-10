from pydantic import BaseModel, ConfigDict, Field

from documents.pdf.assembleur_blocs_json import TypeDeBlocOcr


class _BlocOcrJson(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    type_de_bloc: TypeDeBlocOcr = Field(strict=False)
    code_recommandation: str | None
    titre: str | None
    texte: str
    niveau: int | None
    est_une_continuation: bool
    elements_de_liste: list[str] | None


class _ReponseOcrJson(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    blocs: list[_BlocOcrJson]


SCHEMA_BLOCS_OCR: dict[str, object] = _ReponseOcrJson.model_json_schema()
