import pytest

from documents.docling.pages_avec_texte import (
    identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte,
)


class PageDeTest:
    def __init__(self, texte: str):
        self.texte = texte

    def get_textpage(self):
        return self

    def get_text_bounded(self):
        return self.texte


class PdfDeTest:
    def __init__(self, textes_par_page: list[str]):
        self.pages = [PageDeTest(texte) for texte in textes_par_page]

    def __len__(self):
        return len(self.pages)

    def __getitem__(self, numero_page: int):
        return self.pages[numero_page]


@pytest.mark.parametrize(
    "textes_par_page, plages_attendues",
    [
        (["Texte suffisamment long", "", "Autre texte suffisamment long"], [(1, 1), (3, 3)]),
        (["Texte suffisamment long", "Autre texte suffisamment long"], None),
        (["", ""], []),
    ],
)
def test_identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte(
    textes_par_page,
    plages_attendues,
):
    def ouvre_pdf(_: str):
        return PdfDeTest(textes_par_page)

    assert (
        identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte(
            "document.pdf", ouvre_pdf=ouvre_pdf
        )
        == plages_attendues
    )


def test_identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte_retourne_none_en_cas_d_erreur():
    def ouvre_pdf(_: str):
        raise ValueError("PDF invalide")

    assert (
        identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte(
            "document.pdf", ouvre_pdf=ouvre_pdf
        )
        is None
    )
