import pytest

from documents.pdf.assembleur_blocs_json import (
    AssembleurDeBlocsJson,
    PageOcr,
    TypeDeBlocOcr,
)


def _une_page(*blocs, numero_page=1):
    return numero_page, blocs


def _un_paragraphe(texte, est_une_continuation=False):
    return {"texte": texte, "est_une_continuation": est_une_continuation}


def _un_titre(titre, niveau, texte=""):
    return {
        "type_de_bloc": TypeDeBlocOcr.TITRE,
        "titre": titre,
        "texte": texte,
        "niveau": niveau,
    }


def _une_liste(texte, elements=(), est_une_continuation=False):
    return {
        "type_de_bloc": TypeDeBlocOcr.LISTE,
        "texte": texte,
        "elements_de_liste": elements,
        "est_une_continuation": est_une_continuation,
    }


def _une_recommandation(code, titre, texte, elements=(), est_une_continuation=False):
    return {
        "type_de_bloc": TypeDeBlocOcr.RECOMMANDATION,
        "code": code,
        "titre": titre,
        "texte": texte,
        "elements_de_liste": elements,
        "est_une_continuation": est_une_continuation,
    }


def _un_tableau(texte):
    return {
        "type_de_bloc": TypeDeBlocOcr.TABLEAU,
        "texte": texte,
    }


@pytest.fixture
def assemble_les_blocs(un_bloc_ocr_json, un_resultat_ocr):
    def _assemble(*definitions, nombre_de_pages=None):
        pages_ocr = tuple(
            PageOcr(
                numero_page=numero_page,
                blocs=tuple(
                    un_bloc_ocr_json(**proprietes)
                    for proprietes in proprietes_des_blocs
                ),
            )
            for numero_page, proprietes_des_blocs in definitions
        )
        dernier_numero_de_page = max(numero_page for numero_page, _ in definitions)
        resultat_ocr = un_resultat_ocr(
            pages_ocr=pages_ocr,
            nombre_de_pages=nombre_de_pages or dernier_numero_de_page,
        )
        return AssembleurDeBlocsJson().assemble(resultat_ocr)

    return _assemble


def verifie_un_bloc(blocs, texte_attendu):
    assert len(blocs) == 1
    assert blocs[0].texte == texte_attendu


def verifie_deux_blocs(blocs, premier_texte, deuxieme_texte):
    assert len(blocs) == 2
    assert blocs[0].texte == premier_texte
    assert blocs[1].texte == deuxieme_texte


def test_conserve_l_ordre_des_blocs_d_une_page(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            {"texte": "Premier paragraphe"},
            {"texte": "Deuxième paragraphe"},
            {"texte": "Troisième paragraphe"},
        )
    )

    assert len(blocs_indexables) == 3
    assert blocs_indexables[0].texte == "Premier paragraphe"
    assert blocs_indexables[1].texte == "Deuxième paragraphe"
    assert blocs_indexables[2].texte == "Troisième paragraphe"


def test_cree_un_bloc_indexable_avec_son_type_son_code_et_son_titre(
    assemble_les_blocs,
):
    bloc_indexable = assemble_les_blocs(
        _une_page(
            _une_recommandation(
                "R24", "Protéger le système", "Le système doit être protégé."
            )
        )
    )[0]

    assert bloc_indexable.texte == (
        "R24\nProtéger le système\nLe système doit être protégé."
    )
    assert bloc_indexable.contexte.type_de_bloc == "recommandation"
    assert bloc_indexable.contexte.code_recommandation == "R24"
    assert bloc_indexable.contexte.titre == "Protéger le système"


def test_conserve_les_pages_couvertes_par_des_blocs_distincts(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Page 1"}),
        _une_page({"texte": "Page 3"}, numero_page=3),
        nombre_de_pages=3,
    )

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].page_debut == 1
    assert blocs_indexables[0].page_fin == 1
    assert blocs_indexables[0].pages_couvertes == (1,)
    assert blocs_indexables[1].page_debut == 3
    assert blocs_indexables[1].page_fin == 3
    assert blocs_indexables[1].pages_couvertes == (3,)


def test_assemble_les_pages_dans_l_ordre_de_leur_numero(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Page 2"}, numero_page=2),
        _une_page({"texte": "Page 1"}),
    )

    assert [bloc.texte for bloc in blocs_indexables] == ["Page 1", "Page 2"]


def test_conserve_un_titre_sans_contenu_avant_une_continuation(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (un_bloc_ocr_json(texte="Début"),),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="Nouvelle section",
                    texte="",
                ),
                un_bloc_ocr_json(texte="Suite", est_une_continuation=True),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert [bloc.texte for bloc in blocs_indexables] == [
        "Début",
        "Nouvelle section\nSuite",
    ]


def test_fusionne_un_paragraphe_qui_continue_sur_la_page_suivante(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Début"}),
        _une_page(_un_paragraphe("Suite", est_une_continuation=True), numero_page=2),
    )

    verifie_un_bloc(blocs_indexables, "Début\nSuite")
    assert blocs_indexables[0].pages_couvertes == (1, 2)
    assert blocs_indexables[0].page_debut == 1
    assert blocs_indexables[0].page_fin == 2


def test_fusionne_un_paragraphe_coupe_sans_marqueur_de_continuation(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Le coût du chiffrement"}),
        _une_page({"texte": "est généralement négligeable."}, numero_page=2),
    )

    verifie_un_bloc(
        blocs_indexables,
        "Le coût du chiffrement\nest généralement négligeable.",
    )
    assert blocs_indexables[0].pages_couvertes == (1, 2)


def test_fusionne_la_suite_d_une_recommandation_sur_la_page_suivante(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("3 Recommandations", 1),
            _un_paragraphe("Introduction."),
            _un_titre("3.2 Opérations", 2),
            _une_recommandation(
                "R23",
                "Définir une stratégie de restauration",
                "La stratégie tient compte des services d'infrastructure, comme l'an-",
            ),
            numero_page=8,
        ),
        _une_page(
            _un_paragraphe("nuaire, le DNS et le NTP."),
            numero_page=9,
        ),
        nombre_de_pages=9,
    )

    bloc_recommandation = blocs_indexables[-1]
    assert bloc_recommandation.texte == (
        "3.2 Opérations\n"
        "R23\n"
        "Définir une stratégie de restauration\n"
        "La stratégie tient compte des services d'infrastructure, comme l'an-\n"
        "nuaire, le DNS et le NTP."
    )
    assert bloc_recommandation.contexte.type_de_bloc == "recommandation"
    assert bloc_recommandation.contexte.code_recommandation == "R23"
    assert bloc_recommandation.contexte.chemin_des_sections == (
        "3 Recommandations",
        "3.2 Opérations",
    )
    assert bloc_recommandation.page_debut == 8
    assert bloc_recommandation.page_fin == 9
    assert bloc_recommandation.pages_couvertes == (8, 9)


def test_fusionne_la_liste_d_une_recommandation_sur_la_page_suivante(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(
                numero_page=29,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R33",
                        titre="Durcir les mesures de sécurité",
                        texte=(
                            "Les mesures suivantes sont recommandées :\n"
                            "- Protéger les données.\n- Contrôler les accès."
                        ),
                    ),
                ),
            ),
            PageOcr(
                numero_page=30,
                blocs=(
                    un_bloc_ocr_json(texte="- Sécuriser les services exposés."),
                ),
            ),
        ),
        nombre_de_pages=30,
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == (
        "R33\nDurcir les mesures de sécurité\n"
        "Les mesures suivantes sont recommandées :\n"
        "- Protéger les données.\n- Contrôler les accès.\n"
        "- Sécuriser les services exposés."
    )
    assert blocs_indexables[0].contexte.type_de_bloc == "recommandation"
    assert blocs_indexables[0].contexte.code_recommandation == "R33"
    assert blocs_indexables[0].page_debut == 29
    assert blocs_indexables[0].page_fin == 30
    assert blocs_indexables[0].pages_couvertes == (29, 30)


def test_ne_fusionne_pas_une_liste_independante_apres_une_recommandation(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(
                numero_page=29,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R33",
                        titre="Durcir les mesures de sécurité",
                        texte="La recommandation est terminée.",
                    ),
                ),
            ),
            PageOcr(
                numero_page=30,
                blocs=(un_bloc_ocr_json(texte="- Une nouvelle mesure."),),
            ),
        ),
        nombre_de_pages=30,
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == (
        "R33\nDurcir les mesures de sécurité\nLa recommandation est terminée."
    )
    assert blocs_indexables[1].texte == "- Une nouvelle mesure."


@pytest.mark.parametrize(
    "definitions, premier_texte, deuxieme_texte",
    [
        pytest.param(
            (
                _une_page({"texte": "Le paragraphe est terminé."}),
                _une_page({"texte": "Une nouvelle information."}, numero_page=2),
            ),
            "Le paragraphe est terminé.",
            "Une nouvelle information.",
            id="phrase_terminee",
        ),
        pytest.param(
            (
                _une_page({"texte": "Le paragraphe semble incomplet"}),
                _une_page({"texte": "Nouvelle information."}, numero_page=2),
            ),
            "Le paragraphe semble incomplet",
            "Nouvelle information.",
            id="nouvelle_phrase",
        ),
        pytest.param(
            (
                _une_page(
                    {"texte": "Premier"},
                    _un_paragraphe("Deuxième", est_une_continuation=True),
                ),
            ),
            "Premier",
            "Deuxième",
            id="paragraphes_sur_meme_page",
        ),
        pytest.param(
            (
                _une_page({"texte": "Le paragraphe semble incomplet"}),
                _une_page(numero_page=2),
                _une_page({"texte": "est continué ici."}, numero_page=3),
            ),
            "Le paragraphe semble incomplet",
            "est continué ici.",
            id="page_vide",
        ),
        pytest.param(
            (
                _une_page({"texte": "Le paragraphe semble incomplet"}),
                _une_page(numero_page=2),
                _une_page(
                    _un_paragraphe("est continué ici.", est_une_continuation=True),
                    numero_page=3,
                ),
            ),
            "Le paragraphe semble incomplet",
            "est continué ici.",
            id="page_vide_avec_marqueur",
        ),
        pytest.param(
            (
                _une_page({"texte": "Début"}),
                _une_page(
                    _un_paragraphe("Suite", est_une_continuation=True),
                    numero_page=3,
                ),
            ),
            "Début",
            "Suite",
            id="page_absente",
        ),
    ],
)
def test_ne_fusionne_pas_les_paragraphes_quand_une_regle_l_interdit(
    definitions,
    premier_texte,
    deuxieme_texte,
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(*definitions)

    verifie_deux_blocs(blocs_indexables, premier_texte, deuxieme_texte)


def test_ne_fusionne_pas_un_paragraphe_apres_un_titre(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Début"}),
        _une_page(
            _un_titre("Nouvelle section", 1, "Nouvelle section"),
            _un_paragraphe("Nouveau contenu", est_une_continuation=True),
            numero_page=2,
        ),
    )

    verifie_deux_blocs(
        blocs_indexables,
        "Début",
        "Nouvelle section\nNouveau contenu",
    )


def test_met_a_jour_le_chemin_des_sections_selon_le_niveau_du_titre(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("Section 1", 1, "Section 1"),
            _un_titre("Section 1.1", 2, "Section 1.1"),
            {"texte": "Contenu"},
        )
    )

    assert blocs_indexables[-1].contexte.chemin_des_sections == (
        "Section 1",
        "Section 1.1",
    )


def test_deduit_le_niveau_d_un_titre_numerote_meme_si_le_niveau_ocr_est_errone(
    assemble_les_blocs,
):
    titre = "3.3 Protection des données"
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("3 Recommandations", 1),
            _un_paragraphe("Introduction."),
            _un_titre(titre, 1),
            _un_paragraphe("Les sauvegardes doivent être protégées."),
        )
    )

    bloc_indexable = blocs_indexables[-1]
    assert bloc_indexable.contexte.chemin_des_sections == (
        "3 Recommandations",
        titre,
    )


def test_conserve_le_titre_dans_le_premier_bloc_de_la_section(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("Section", 1, "Section"),
            {"texte": "Premier paragraphe"},
            {"texte": "Deuxième paragraphe"},
        )
    )

    verifie_deux_blocs(
        blocs_indexables,
        "Section\nPremier paragraphe",
        "Deuxième paragraphe",
    )


def test_cree_un_bloc_autonome_pour_un_titre_sans_contenu(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page(_un_titre("Section vide", 1, "Section vide"))
    )

    verifie_un_bloc(blocs_indexables, "Section vide")


def test_conserve_un_titre_place_par_erreur_sur_un_paragraphe(assemble_les_blocs):
    titre = "6.1.2 ESP : confidentialité, intégrité et authentification des paquets"
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("6 Fonctionnement d’IPsec", 1),
            _un_titre("6.1 Services fournis par IPsec", 2),
            {
                "type_de_bloc": TypeDeBlocOcr.PARAGRAPHE,
                "titre": titre,
                "texte": "Le protocole ESP protège les données.",
                "niveau": 0,
            },
        )
    )

    bloc_indexable = blocs_indexables[-1]
    assert bloc_indexable.texte == f"{titre}\nLe protocole ESP protège les données."
    assert bloc_indexable.contexte.chemin_des_sections == (
        "6 Fonctionnement d’IPsec",
        "6.1 Services fournis par IPsec",
        titre,
    )


def test_promeut_un_titre_numerote_mal_classe_dans_le_meme_chapitre(
    assemble_les_blocs,
):
    titre = "2.4 Authentification multifacteur"
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("2 Authentification", 1),
            _un_titre("2.3 Mots de passe", 2),
            {
                "type_de_bloc": TypeDeBlocOcr.PARAGRAPHE,
                "titre": titre,
                "texte": "Le contenu de la section.",
            },
        )
    )

    bloc_indexable = blocs_indexables[-1]
    assert bloc_indexable.texte == f"{titre}\nLe contenu de la section."
    assert bloc_indexable.contexte.chemin_des_sections == (
        "2 Authentification",
        titre,
    )


def test_conserve_un_titre_local_lorsque_le_chapitre_est_incoherent(
    assemble_les_blocs,
):
    titre = "6.1 Élément sans rapport"
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("2 Authentification", 1),
            _un_titre("2.4 Authentification multifacteur", 2),
            {
                "type_de_bloc": TypeDeBlocOcr.PARAGRAPHE,
                "titre": titre,
                "texte": "Le contenu reste local.",
            },
        )
    )

    bloc_indexable = blocs_indexables[-1]
    assert bloc_indexable.texte == (
        "2.4 Authentification multifacteur\n"
        f"{titre}\nLe contenu reste local."
    )
    assert bloc_indexable.contexte.titre == titre
    assert bloc_indexable.contexte.chemin_des_sections == (
        "2 Authentification",
        "2.4 Authentification multifacteur",
    )


def test_conserve_un_titre_non_numerote_comme_information_locale(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre("2 Authentification", 1),
            {
                "type_de_bloc": TypeDeBlocOcr.PARAGRAPHE,
                "titre": "Attention",
                "texte": "Un encadré important.",
            },
        )
    )

    bloc_indexable = blocs_indexables[-1]
    assert bloc_indexable.texte == (
        "2 Authentification\nAttention\nUn encadré important."
    )
    assert bloc_indexable.contexte.titre == "Attention"
    assert bloc_indexable.contexte.chemin_des_sections == ("2 Authentification",)


def test_conserve_la_table_des_matieres_dans_un_unique_bloc(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            {
                "type_de_bloc": TypeDeBlocOcr.TABLE_DES_MATIERES,
                "titre": "Sommaire",
                "texte": "1 Introduction\n2 Authentification",
            }
        )
    )

    verifie_un_bloc(blocs_indexables, "1 Introduction\n2 Authentification")
    assert blocs_indexables[0].contexte.type_de_bloc == "table_des_matieres"
    assert blocs_indexables[0].contexte.chemin_des_sections == ()


def test_ne_fusionne_pas_une_recommandation_avec_un_paragraphe(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Contexte"}),
        _une_page(
            _une_recommandation(
                "R2", "Recommandation", "Contenu", est_une_continuation=True
            ),
            numero_page=2,
        ),
    )

    assert len(blocs_indexables) == 2
    assert blocs_indexables[1].contexte.code_recommandation == "R2"


@pytest.mark.parametrize(
    "definitions, premier_texte, deuxieme_texte",
    [
        pytest.param(
            (_une_page(_une_liste("Premier élément\nDeuxième élément", ("Premier élément", "Deuxième élément"))),),
            "Premier élément\nDeuxième élément",
            None,
            id="liste_autonome",
        ),
        pytest.param(
            (
                _une_page({"type_de_bloc": TypeDeBlocOcr.LISTE, "texte": "Premier élément"}),
                _une_page(_une_liste("Deuxième élément", est_une_continuation=True), numero_page=2),
            ),
            "Premier élément\nDeuxième élément",
            None,
            id="liste_continuée",
        ),
        pytest.param(
            (
                _une_page(_une_liste("Première liste")),
                _une_page(_une_liste("Deuxième liste"), numero_page=2),
            ),
            "Première liste",
            "Deuxième liste",
            id="listes_distinctes",
        ),
        pytest.param(
            (
                _une_page(
                    _une_liste("- Première recommandation\n- Deuxième recommandation"),
                    _une_liste("- Première recommandation\n- Deuxième recommandation"),
                ),
            ),
            "- Première recommandation\n- Deuxième recommandation",
            None,
            id="liste_identique_repetee",
        ),
    ],
)
def test_assemble_les_listes_selon_leur_relation(
    definitions,
    premier_texte,
    deuxieme_texte,
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(*definitions)

    if deuxieme_texte is None:
        verifie_un_bloc(blocs_indexables, premier_texte)
    else:
        verifie_deux_blocs(blocs_indexables, premier_texte, deuxieme_texte)
    assert blocs_indexables[0].contexte.type_de_bloc == "liste"


@pytest.mark.parametrize(
    "definitions, texte_attendu",
    [
        pytest.param(
            (
                _une_page(
                    {
                        "texte": "Introduction de la liste",
                        "elements_de_liste": ("Premier élément", "Deuxième élément"),
                    }
                ),
            ),
            "Introduction de la liste\n- Premier élément\n- Deuxième élément",
            id="introduction_et_puces_dans_un_bloc",
        ),
        pytest.param(
            (
                _une_page(
                    {"texte": "Les raisons sont les suivantes :"},
                    _une_liste("", ("Première raison", "Deuxième raison")),
                ),
            ),
            "Les raisons sont les suivantes :\n- Première raison\n- Deuxième raison",
            id="introduction_et_bloc_de_liste_separe",
        ),
    ],
)
def test_conserve_une_introduction_et_ses_elements_de_liste(
    definitions,
    texte_attendu,
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(*definitions)

    verifie_un_bloc(blocs_indexables, texte_attendu)
    assert blocs_indexables[0].contexte.type_de_bloc == "liste"
    assert blocs_indexables[0].pages_couvertes == (1,)


def test_conserve_les_elements_de_liste_d_une_recommandation(assemble_les_blocs):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _une_recommandation(
                "R2",
                "Protéger les données",
                "La recommandation contient les actions suivantes :",
                ("Première action", "Deuxième action"),
            )
        )
    )

    verifie_un_bloc(
        blocs_indexables,
        "R2\nProtéger les données\n"
        "La recommandation contient les actions suivantes :\n"
        "- Première action\n- Deuxième action",
    )
    assert blocs_indexables[0].contexte.type_de_bloc == "recommandation"


def test_conserve_le_tableau_html_sans_transformation(assemble_les_blocs):
    texte_html = (
        "<table><thead><tr><th>Nom</th><th>Valeur</th></tr></thead>"
        "<tbody><tr><td>Risque</td><td>Élevé</td></tr></tbody></table>"
    )

    blocs_indexables = assemble_les_blocs(_une_page(_un_tableau(texte_html)))

    verifie_un_bloc(blocs_indexables, texte_html)
    assert blocs_indexables[0].contexte.type_de_bloc == "tableau"


@pytest.mark.parametrize(
    "proprietes_du_bloc_ignore, texte_attendu",
    [
        pytest.param(
            {"type_de_bloc": TypeDeBlocOcr.PIED_DE_PAGE, "texte": "1"},
            "Contenu utile",
            id="pied_de_page",
        ),
        pytest.param({"texte": ""}, "Contenu utile", id="bloc_vide"),
    ],
)
def test_ignore_les_blocs_sans_contenu_indexable(
    proprietes_du_bloc_ignore,
    texte_attendu,
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(proprietes_du_bloc_ignore, {"texte": texte_attendu})
    )

    verifie_un_bloc(blocs_indexables, texte_attendu)


def test_fusionne_la_fin_d_une_puce_avec_le_paragraphe_de_la_page_suivante(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(_une_liste("- Attaquant hors ligne : les données sont protégées par")),
        _une_page(
            {"texte": "exemple en utilisant des fonctions de hachage dédiées."},
            numero_page=2,
        ),
    )

    verifie_un_bloc(
        blocs_indexables,
        "- Attaquant hors ligne : les données sont protégées par\n"
        "exemple en utilisant des fonctions de hachage dédiées.",
    )
    assert blocs_indexables[0].page_debut == 1
    assert blocs_indexables[0].page_fin == 2
    assert blocs_indexables[0].pages_couvertes == (1, 2)


@pytest.mark.parametrize("marqueur", ["■", "•", "▪", "◦", "‣", "- "])
def test_normalise_les_marqueurs_de_liste(
    marqueur,
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(texte=f"{marqueur} Élément"),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert blocs_indexables[0].texte == "- Élément"


def test_conserve_un_tableau_comme_un_bloc(
    un_bloc_ocr_json,
    un_resultat_ocr,
): 
    bloc_tableau = un_bloc_ocr_json(
        type_de_bloc=TypeDeBlocOcr.TABLEAU,
        texte="",
        lignes_de_tableau=(("Nom", "Valeur"), ("Risque", "Élevé")),
    )
    resultat_ocr = un_resultat_ocr(
        ((bloc_tableau,),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].contexte.type_de_bloc == "tableau"
    assert blocs_indexables[0].texte == "Nom\tValeur\nRisque\tÉlevé"


def test_conserve_les_lignes_et_cellules_d_un_tableau(
    un_bloc_ocr_json,
    un_resultat_ocr,
): 
    bloc_tableau = un_bloc_ocr_json(
        type_de_bloc=TypeDeBlocOcr.TABLEAU,
        texte="Contenu du tableau",
        lignes_de_tableau=(("Nom", "Valeur"),),
    )
    resultat_ocr = un_resultat_ocr(
        ((bloc_tableau,),)
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_tableau.lignes_de_tableau == (("Nom", "Valeur"),)
    assert bloc_indexable.texte == "Contenu du tableau\nNom\tValeur"


def test_fusionne_la_puce_en_debut_de_page_avec_la_liste_precedente(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(
            {
                "texte": "Introduction de la liste",
                "elements_de_liste": ("Premier élément",),
            }
        ),
        _une_page({"texte": "■ Deuxième élément"}, numero_page=2),
    )

    verifie_un_bloc(
        blocs_indexables,
        "Introduction de la liste\n- Premier élément\n- Deuxième élément",
    )
    assert blocs_indexables[0].pages_couvertes == (1, 2)


def test_ne_fusionne_pas_une_puce_en_debut_de_page_sans_liste_precedente(
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page({"texte": "Paragraphe"}),
        _une_page({"texte": "■ Nouvelle liste"}, numero_page=2),
    )

    verifie_deux_blocs(blocs_indexables, "Paragraphe", "- Nouvelle liste")


@pytest.mark.parametrize(
    "numero, libelle, niveau",
    [
        pytest.param("5", "Recommandations", 1, id="titre_numerote_5"),
        pytest.param(
            "5.1",
            "Recommandations générales",
            2,
            id="titre_numerote_5_1",
        ),
    ],
)
def test_conserve_le_libelle_d_un_titre_numerote(
    numero,
    libelle,
    niveau,
    assemble_les_blocs,
):
    blocs_indexables = assemble_les_blocs(
        _une_page(_un_titre(numero, niveau, libelle))
    )

    verifie_un_bloc(blocs_indexables, f"{numero} {libelle}")
    assert blocs_indexables[0].contexte.chemin_des_sections == (f"{numero} {libelle}",)


def test_conserve_le_paragraphe_associe_a_un_titre_deja_complet(
    assemble_les_blocs,
):
    titre = "5.2 Recommandations pour l'entraînement"
    blocs_indexables = assemble_les_blocs(
        _une_page(
            _un_titre(
                titre,
                2,
                "Le paragraphe qui suit le titre doit être conservé.",
            )
        )
    )

    verifie_un_bloc(
        blocs_indexables,
        f"{titre}\nLe paragraphe qui suit le titre doit être conservé.",
    )
    assert blocs_indexables[0].contexte.section == titre
