import re
from dataclasses import replace

from documents.pdf.modeles_ocr_json import BlocOcr, TypeDeBlocOcr


class _NormalisateurDeBlocsOcr:
    def doit_traiter(self, bloc_ocr: BlocOcr) -> bool:
        return bloc_ocr.type_de_bloc != TypeDeBlocOcr.PIED_DE_PAGE

    def normalise(
        self,
        bloc_ocr: BlocOcr,
        chemin_des_sections: list[str],
    ) -> BlocOcr:
        if not self._doit_promouvoir_le_titre_local_en_section(
            bloc_ocr,
            chemin_des_sections,
        ):
            return bloc_ocr
        return replace(bloc_ocr, type_de_bloc=TypeDeBlocOcr.TITRE)

    def est_un_bloc_a_ignorer(self, bloc_ocr: BlocOcr) -> bool:
        texte = bloc_ocr.texte.strip()
        if bloc_ocr.type_de_bloc == TypeDeBlocOcr.LISTE:
            return not texte and not bloc_ocr.elements_de_liste
        if bloc_ocr.type_de_bloc == TypeDeBlocOcr.TABLEAU:
            return not texte and not bloc_ocr.lignes_de_tableau
        return not texte and not bloc_ocr.titre and not bloc_ocr.code

    def prepare_le_texte_indexable(self, bloc_ocr: BlocOcr) -> str:
        texte = bloc_ocr.texte.strip()
        if self.est_une_puce_de_liste(texte):
            texte = self.formate_l_element_de_liste(texte)
        elements_de_texte = {
            self.retire_le_marqueur_de_liste(ligne) for ligne in texte.splitlines()
        }
        parties = [texte]
        parties.extend(
            self.formate_l_element_de_liste(element)
            for element in bloc_ocr.elements_de_liste
            if self.retire_le_marqueur_de_liste(element) not in elements_de_texte
        )
        parties.extend(
            "\t".join(cellule.strip() for cellule in ligne)
            for ligne in bloc_ocr.lignes_de_tableau
        )
        texte = "\n".join(partie for partie in dict.fromkeys(parties) if partie)
        if bloc_ocr.type_de_bloc != TypeDeBlocOcr.RECOMMANDATION:
            return texte

        parties_recommandation = [
            partie
            for partie in (bloc_ocr.code, bloc_ocr.titre, texte)
            if partie and partie.strip()
        ]
        return "\n".join(dict.fromkeys(parties_recommandation))

    def separe_le_titre_du_texte(
        self,
        titre: str | None,
        texte: str,
    ) -> tuple[str, str]:
        titre_nettoye = (titre or "").strip()
        texte_nettoye = texte.strip()
        if not titre_nettoye:
            return texte_nettoye, ""
        if re.fullmatch(r"\d+(?:\.\d+)*", titre_nettoye) and texte_nettoye:
            return f"{titre_nettoye} {texte_nettoye}", ""
        if texte_nettoye == titre_nettoye:
            return titre_nettoye, ""
        return titre_nettoye, texte_nettoye

    def determine_le_type_de_bloc_indexable(
        self,
        bloc_ocr: BlocOcr,
    ) -> TypeDeBlocOcr:
        if bloc_ocr.type_de_bloc in {
            TypeDeBlocOcr.RECOMMANDATION,
            TypeDeBlocOcr.TABLEAU,
            TypeDeBlocOcr.TABLE_DES_MATIERES,
        }:
            return bloc_ocr.type_de_bloc
        if bloc_ocr.elements_de_liste or self.est_une_puce_de_liste(bloc_ocr.texte):
            return TypeDeBlocOcr.LISTE
        return bloc_ocr.type_de_bloc

    def formate_l_element_de_liste(self, element: str) -> str:
        element_nettoye = self.retire_le_marqueur_de_liste(element)
        return f"- {element_nettoye}"

    def est_une_puce_de_liste(self, texte: str) -> bool:
        texte_nettoye = texte.lstrip()
        return texte_nettoye.startswith(("■", "•", "▪", "◦", "‣", "- "))

    def retire_le_marqueur_de_liste(self, texte: str) -> str:
        texte_nettoye = texte.strip()
        if texte_nettoye.startswith(("■", "•", "▪", "◦", "‣")):
            return texte_nettoye[1:].lstrip()
        if texte_nettoye.startswith("- "):
            return texte_nettoye[2:].lstrip()
        return texte_nettoye

    def _doit_promouvoir_le_titre_local_en_section(
        self,
        bloc_ocr: BlocOcr,
        chemin_des_sections: list[str],
    ) -> bool:
        if bloc_ocr.type_de_bloc != TypeDeBlocOcr.PARAGRAPHE or not bloc_ocr.titre:
            return False
        numero_de_section = _extrait_le_numero_de_section(bloc_ocr.titre)
        if numero_de_section is None:
            return False
        niveau = numero_de_section.count(".") + 1
        chapitre_courant = _extrait_le_chapitre_courant(chemin_des_sections)
        chapitre_du_titre = numero_de_section.split(".")[0]
        if chapitre_courant is None:
            return niveau == 1
        if niveau == 1:
            return int(chapitre_du_titre) in {
                int(chapitre_courant),
                int(chapitre_courant) + 1,
            }
        return chapitre_du_titre == chapitre_courant


def _extrait_le_numero_de_section(titre: str) -> str | None:
    correspondance = re.match(r"\s*(\d+(?:\.\d+)*)\b", titre)
    if correspondance is None:
        return None
    return correspondance.group(1)


def _extrait_le_chapitre_courant(chemin_des_sections: list[str]) -> str | None:
    for section in chemin_des_sections:
        numero_de_section = _extrait_le_numero_de_section(section)
        if numero_de_section is not None:
            return numero_de_section.split(".")[0]
    return None
