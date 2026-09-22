import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

from documents.page import BlocPage


MARQUEUR_DEBUT_CONTEXTE_DOCUMENTAIRE = "[Contexte documentaire]"
MARQUEUR_FIN_CONTEXTE_DOCUMENTAIRE = "[/Contexte documentaire]"


def construit_le_contexte_documentaire(
    nom_document: str,
    sommaire_hierarchique: dict[str, dict],
    bloc: BlocPage,
) -> str | None:
    contexte = bloc.contexte
    if contexte is None:
        return None
    chemin = resout_le_chemin_de_sections(
        sommaire_hierarchique,
        titre=contexte.titre,
        chemin_des_sections=contexte.chemin_des_sections,
    )
    if not chemin:
        return None
    return "\n".join(
        (
            MARQUEUR_DEBUT_CONTEXTE_DOCUMENTAIRE,
            f"Document : {_normalise_le_nom_document(nom_document)}",
            f"Sections : {' > '.join(chemin)}",
            MARQUEUR_FIN_CONTEXTE_DOCUMENTAIRE,
        )
    )


def enrichit_le_contenu_indexe(
    nom_document: str,
    sommaire_hierarchique: dict[str, dict],
    bloc: BlocPage,
) -> str:
    contexte = construit_le_contexte_documentaire(
        nom_document, sommaire_hierarchique, bloc
    )
    if contexte is None:
        return bloc.texte
    return f"{bloc.texte}\n\n{contexte}"


def separe_le_contenu_indexe(contenu: str) -> tuple[str, str | None]:
    suffixe = f"\n{MARQUEUR_FIN_CONTEXTE_DOCUMENTAIRE}"
    prefixe = f"\n\n{MARQUEUR_DEBUT_CONTEXTE_DOCUMENTAIRE}\n"
    if not contenu.endswith(suffixe):
        return contenu, None
    position = contenu.rfind(prefixe, 0, -len(suffixe))
    if position < 0:
        return contenu, None
    debut_contexte = position + len(prefixe)
    fin_contexte = len(contenu) - len(suffixe)
    return contenu[:position], contenu[debut_contexte:fin_contexte]


def resout_le_chemin_de_sections(
    sommaire_hierarchique: dict[str, dict],
    *,
    titre: str | None,
    chemin_des_sections: tuple[str, ...],
) -> tuple[str, ...]:
    chemins_par_titre = _indexe_les_chemins_par_titre(sommaire_hierarchique)
    candidats = (titre, *reversed(chemin_des_sections))

    for candidat in candidats:
        cle = _normalise_un_titre(candidat)
        chemins = chemins_par_titre.get(cle, [])
        if len(chemins) == 1:
            return chemins[0]

    return chemin_des_sections


def _indexe_les_chemins_par_titre(
    sommaire: dict[str, dict],
    parent: tuple[str, ...] = (),
) -> dict[str, list[tuple[str, ...]]]:
    resultat: dict[str, list[tuple[str, ...]]] = {}
    for titre, enfants in sommaire.items():
        chemin = (*parent, titre)
        cle = _normalise_un_titre(titre)
        if cle:
            resultat.setdefault(cle, []).append(chemin)
        for cle_enfant, chemins_enfant in _indexe_les_chemins_par_titre(
            enfants, chemin
        ).items():
            resultat.setdefault(cle_enfant, []).extend(chemins_enfant)
    return resultat


def _normalise_un_titre(titre: str | None) -> str:
    if not titre:
        return ""
    texte = unicodedata.normalize("NFKD", titre)
    texte = "".join(caractere for caractere in texte if not unicodedata.combining(caractere))
    texte = re.sub(
        r"^\s*(?:\d+(?:[./]\d+)*|(?:annexe\s+)?[A-Za-z]\.\d+(?:\.\d+)*)\s*(?:[/.:—-]\s*)?",
        "",
        texte,
    )
    texte = re.sub(r"[^\w]+", " ", texte.casefold())
    return " ".join(texte.split())


def _normalise_le_nom_document(nom_document: str) -> str:
    nom = Path(unquote(nom_document)).stem.replace("_", " ")
    return " ".join(nom.split())
