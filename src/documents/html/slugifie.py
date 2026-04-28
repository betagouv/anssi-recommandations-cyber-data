import re
import unicodedata


def slugifie(texte: str) -> str:
    normalise = unicodedata.normalize("NFD", texte)
    sans_diacritiques = "".join(c for c in normalise if unicodedata.category(c) != "Mn")
    minuscules = sans_diacritiques.lower()
    sans_speciaux = re.sub(r"[^\w\s-]", "", minuscules, flags=re.UNICODE)
    avec_tirets = re.sub(r"[\s_]+", "-", sans_speciaux)
    propre = re.sub(r"-+", "-", avec_tirets).strip("-")
    return propre[:80]
