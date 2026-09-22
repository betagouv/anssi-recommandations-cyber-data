from documents.contexte_documentaire import (
    construit_le_contexte_documentaire,
    enrichit_le_contenu_indexe,
    resout_le_chemin_de_sections,
    separe_le_contenu_indexe,
)
from documents.page import BlocPage, ContexteDuBloc


def test_resout_le_chemin_hierarchique_depuis_un_titre_local_normalise() -> None:
    sommaire: dict[str, dict] = {
        "Cadrage et socle de sécurité": {
            "Atelier 1": {
                "Les participants à l'atelier": {},
            },
        },
    }

    chemin = resout_le_chemin_de_sections(
        sommaire,
        titre="2/ LES PARTICIPANTS À L’ATELIER",
        chemin_des_sections=(),
    )

    assert chemin == (
        "Cadrage et socle de sécurité",
        "Atelier 1",
        "Les participants à l'atelier",
    )


def test_replie_sur_le_chemin_ocr_quand_le_titre_est_ambigu() -> None:
    sommaire: dict[str, dict] = {
        "Partie A": {"Introduction": {}},
        "Partie B": {"Introduction": {}},
    }

    chemin = resout_le_chemin_de_sections(
        sommaire,
        titre="Introduction",
        chemin_des_sections=("Contexte local", "Introduction"),
    )

    assert chemin == ("Contexte local", "Introduction")


def test_construit_un_contexte_avec_nom_de_fichier_normalise() -> None:
    bloc = BlocPage(
        texte="Les rôles des participants.",
        numero_page=20,
        contexte=ContexteDuBloc(
            titre="2/ LES PARTICIPANTS À L’ATELIER",
            chemin_des_sections=("2/ LES PARTICIPANTS À L’ATELIER",),
        ),
    )
    sommaire: dict[str, dict] = {
        "Cadrage et socle de sécurité": {
            "Atelier 1": {"Les participants à l'atelier": {}},
        },
    }

    contexte = construit_le_contexte_documentaire(
        "guide-homologation_securite-web-04-2025.pdf",
        sommaire,
        bloc,
    )

    assert contexte == (
        "[Contexte documentaire]\n"
        "Document : guide homologation securite web 04 2025\n"
        "Sections : Cadrage et socle de sécurité > Atelier 1 > "
        "Les participants à l'atelier\n"
        "[/Contexte documentaire]"
    )


def test_enrichit_le_contenu_indexe_sans_modifier_le_texte_source() -> None:
    bloc = BlocPage(
        texte="Les rôles des participants.",
        numero_page=20,
        contexte=ContexteDuBloc(
            titre="Les participants à l'atelier",
            chemin_des_sections=("Les participants à l'atelier",),
        ),
    )

    contenu = enrichit_le_contenu_indexe(
        "guide_ebios.pdf",
        {"Atelier 1": {"Les participants à l'atelier": {}}},
        bloc,
    )

    assert contenu == (
        "Les rôles des participants.\n\n"
        "[Contexte documentaire]\n"
        "Document : guide ebios\n"
        "Sections : Atelier 1 > Les participants à l'atelier\n"
        "[/Contexte documentaire]"
    )
    assert bloc.texte == "Les rôles des participants."


def test_separe_le_texte_source_du_contexte_documentaire() -> None:
    contenu, contexte = separe_le_contenu_indexe(
        "Les rôles des participants.\n\n"
        "[Contexte documentaire]\n"
        "Document : guide ebios\n"
        "Sections : Atelier 1 > Les participants à l'atelier\n"
        "[/Contexte documentaire]"
    )

    assert contenu == "Les rôles des participants."
    assert contexte == (
        "Document : guide ebios\n"
        "Sections : Atelier 1 > Les participants à l'atelier"
    )


def test_conserve_un_contenu_historique_sans_contexte_documentaire() -> None:
    contenu, contexte = separe_le_contenu_indexe("Un chunk déjà indexé.")

    assert contenu == "Un chunk déjà indexé."
    assert contexte is None
