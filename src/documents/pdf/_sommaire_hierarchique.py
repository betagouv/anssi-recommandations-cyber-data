import re

from documents.pdf.modeles_ocr_json import ResultatOcrPdf, TypeDeBlocOcr


_ENTREE_NUMEROTEE = re.compile(r"\s*(\d+(?:\.\d+)*)\s+(.+?)\s*$")
_ENTREE_ANNEXE = re.compile(r"\s*Annexe\s+([A-Z])\s+(.+?)\s*$", re.IGNORECASE)
_ENTREE_SECTION_ANNEXE = re.compile(
    r"\s*([A-Z])\.(\d+(?:\.\d+)*)\s+(.+?)\s*$",
    re.IGNORECASE,
)
_POINTILLES_ET_PAGINATION = re.compile(r"\s*(?:\.\s*){2,}\d+\s*$")


def extrait_le_sommaire_hierarchique(
    resultat_ocr: ResultatOcrPdf,
) -> dict[str, dict]:
    sommaire: dict[str, dict] = {}
    noeuds_par_numero: dict[str, dict] = {}

    for page in sorted(resultat_ocr.pages, key=lambda page: page.numero_page):
        for bloc in page.blocs:
            if bloc.type_de_bloc != TypeDeBlocOcr.TABLE_DES_MATIERES:
                continue
            for entree in _extrait_les_entrees(bloc.texte, bloc.elements_de_liste):
                entree_numerotee = _extrait_le_numero_et_le_titre(entree)
                if entree_numerotee is None:
                    continue
                numero, titre = entree_numerotee
                titre = _retire_les_pointilles_et_la_pagination(titre)
                if numero in noeuds_par_numero:
                    continue
                parent, separateur, _ = numero.rpartition(".")
                if separateur:
                    enfants_du_parent = noeuds_par_numero.get(parent)
                    if enfants_du_parent is None:
                        continue
                else:
                    enfants_du_parent = sommaire
                if not titre or titre in enfants_du_parent:
                    continue
                enfants: dict[str, dict] = {}
                enfants_du_parent[titre] = enfants
                noeuds_par_numero[numero] = enfants

    return sommaire


def _extrait_les_entrees(
    texte: str, elements_de_liste: tuple[str, ...]
) -> tuple[str, ...]:
    return (
        tuple(ligne for ligne in texte.splitlines() if ligne.strip())
        + elements_de_liste
    )


def _retire_les_pointilles_et_la_pagination(titre: str) -> str:
    return _POINTILLES_ET_PAGINATION.sub("", titre).strip()


def _extrait_le_numero_et_le_titre(entree: str) -> tuple[str, str] | None:
    correspondance = _ENTREE_NUMEROTEE.fullmatch(entree)
    if correspondance is not None:
        return correspondance.group(1), correspondance.group(2)
    correspondance = _ENTREE_ANNEXE.fullmatch(entree)
    if correspondance is not None:
        lettre, titre = correspondance.group(1), correspondance.group(2)
        return lettre.upper(), titre
    correspondance = _ENTREE_SECTION_ANNEXE.fullmatch(entree)
    if correspondance is not None:
        lettre = correspondance.group(1)
        numero = correspondance.group(2)
        titre = correspondance.group(3)
        return f"{lettre.upper()}.{numero}", titre
    return None
