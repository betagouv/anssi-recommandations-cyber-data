import re
from dataclasses import dataclass, replace

from documents.pdf._normalisateur_ocr import _NormalisateurDeBlocsOcr
from documents.pdf.modeles_ocr_json import BlocOcr, TypeDeBlocOcr


@dataclass(frozen=True)
class _TitreEnAttente:
    texte: str
    niveau: int | None
    page: int
    chemin_des_sections: tuple[str, ...]


class _GestionnaireDeSections:
    def __init__(self, normalisateur: _NormalisateurDeBlocsOcr) -> None:
        self._normalisateur = normalisateur
        self.chemin_des_sections: list[str] = []
        self._titre_en_attente: _TitreEnAttente | None = None

    def normalise(self, bloc_ocr: BlocOcr) -> BlocOcr:
        return self._normalisateur.normalise(bloc_ocr, self.chemin_des_sections)

    def doit_finaliser_le_titre_avant(self, bloc_ocr: BlocOcr) -> bool:
        return bloc_ocr.type_de_bloc in {
            TypeDeBlocOcr.TITRE,
            TypeDeBlocOcr.AUTRE,
        }

    def traite_le_titre(
        self,
        bloc_ocr: BlocOcr,
        numero_page: int,
    ) -> tuple[BlocOcr | None, bool, _TitreEnAttente | None]:
        if bloc_ocr.type_de_bloc != TypeDeBlocOcr.TITRE:
            return bloc_ocr, False, None
        titre, texte_suivant = self._normalisateur.separe_le_titre_du_texte(
            bloc_ocr.titre,
            bloc_ocr.texte,
        )
        if not titre:
            return None, False, None
        titre_a_finaliser = self.consomme_le_titre_en_attente()
        niveau_du_titre = _determine_le_niveau_du_titre(titre, bloc_ocr.niveau)
        self.chemin_des_sections = _met_a_jour_le_chemin_des_sections(
            self.chemin_des_sections,
            titre,
            niveau_du_titre,
        )
        self._titre_en_attente = _TitreEnAttente(
            texte=titre,
            niveau=niveau_du_titre,
            page=numero_page,
            chemin_des_sections=tuple(self.chemin_des_sections),
        )
        if not texte_suivant:
            return None, True, titre_a_finaliser
        return (
            replace(
                bloc_ocr,
                type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                code=None,
                titre=None,
                texte=texte_suivant,
                niveau=None,
            ),
            True,
            titre_a_finaliser,
        )

    def consomme_le_titre_en_attente(self) -> _TitreEnAttente | None:
        titre_en_attente = self._titre_en_attente
        self._titre_en_attente = None
        return titre_en_attente


def _met_a_jour_le_chemin_des_sections(
    chemin_des_sections: list[str],
    titre: str,
    niveau: int | None,
) -> list[str]:
    if niveau is None or niveau <= 0:
        return [titre]
    return [*chemin_des_sections[: niveau - 1], titre]


def _determine_le_niveau_du_titre(
    titre: str,
    niveau_du_titre_detecte_par_ocr: int | None,
) -> int | None:
    correspondance = re.match(r"\s*(\d+(?:\.\d+)*)\b", titre)
    if correspondance is not None:
        return correspondance.group(1).count(".") + 1
    if (
        niveau_du_titre_detecte_par_ocr is not None
        and niveau_du_titre_detecte_par_ocr > 0
    ):
        return niveau_du_titre_detecte_par_ocr
    return None
