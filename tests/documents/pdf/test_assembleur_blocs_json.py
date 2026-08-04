import pytest

from documents.pdf.assembleur_blocs_json import (
    AssembleurDeBlocsJson,
    BlocOcr,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)


def test_conserve_les_blocs_distincts_d_une_meme_page(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(texte="Premier paragraphe"),
            un_bloc_ocr_json(texte="Deuxième paragraphe"),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Premier paragraphe"
    assert blocs_indexables[1].texte == "Deuxième paragraphe"


def test_conserve_l_ordre_des_blocs_d_une_page(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(texte="Premier"),
            un_bloc_ocr_json(texte="Deuxième"),
            un_bloc_ocr_json(texte="Troisième"),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 3
    assert blocs_indexables[0].texte == "Premier"
    assert blocs_indexables[1].texte == "Deuxième"
    assert blocs_indexables[2].texte == "Troisième"


def test_cree_un_bloc_indexable_avec_son_type_son_code_et_son_titre(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                code="R24",
                titre="Protéger le système",
                texte="Le système doit être protégé.",
            ),
        ),)
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == (
        "R24\nProtéger le système\nLe système doit être protégé."
    )
    assert bloc_indexable.contexte.type_de_bloc == "recommandation"
    assert bloc_indexable.contexte.code_recommandation == "R24"
    assert bloc_indexable.contexte.titre == "Protéger le système"


def test_conserve_les_pages_couvertes_par_un_bloc(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Page 1"),)),
            PageOcr(numero_page=3, blocs=(un_bloc_ocr_json(texte="Page 3"),)),
        ),
        nombre_de_pages=3,
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].page_debut == 1
    assert blocs_indexables[0].page_fin == 1
    assert blocs_indexables[0].pages_couvertes == (1,)
    assert blocs_indexables[1].page_debut == 3
    assert blocs_indexables[1].page_fin == 3
    assert blocs_indexables[1].pages_couvertes == (3,)


def test_assemble_les_pages_dans_l_ordre_de_leur_numero(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(numero_page=2, blocs=(un_bloc_ocr_json(texte="Page 2"),)),
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Page 1"),)),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

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
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (un_bloc_ocr_json(texte="Début"),),
            (
                un_bloc_ocr_json(
                    texte="Suite",
                    est_une_continuation=True,
                ),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == "Début\nSuite"
    assert blocs_indexables[0].pages_couvertes == (1, 2)
    assert blocs_indexables[0].page_debut == 1
    assert blocs_indexables[0].page_fin == 2


def test_fusionne_un_paragraphe_coupe_sans_marqueur_de_continuation(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (un_bloc_ocr_json(texte="Le coût du chiffrement"),),
            (un_bloc_ocr_json(texte="est généralement négligeable."),),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == (
        "Le coût du chiffrement\nest généralement négligeable."
    )
    assert blocs_indexables[0].pages_couvertes == (1, 2)


def test_fusionne_la_suite_d_une_recommandation_sur_la_page_suivante(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(
                numero_page=8,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                        titre="3 Recommandations",
                        texte="",
                        niveau=1,
                    ),
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                        titre="3.2 Opérations",
                        texte="",
                        niveau=2,
                    ),
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R23",
                        titre="Définir une stratégie de restauration",
                        texte=(
                            "La stratégie tient compte des services "
                            "d'infrastructure, comme l'an-"
                        ),
                    ),
                ),
            ),
            PageOcr(
                numero_page=9,
                blocs=(un_bloc_ocr_json(texte="nuaire, le DNS et le NTP."),),
            ),
        ),
        nombre_de_pages=9,
    )

    bloc_recommandation = AssembleurDeBlocsJson().assemble(resultat_ocr)[-1]

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


def test_ne_fusionne_pas_un_paragraphe_apres_une_phrase_terminee(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (un_bloc_ocr_json(texte="Le paragraphe est terminé."),),
            (un_bloc_ocr_json(texte="Une nouvelle information."),),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Le paragraphe est terminé."
    assert blocs_indexables[1].texte == "Une nouvelle information."


def test_ne_fusionne_pas_un_paragraphe_commencant_une_nouvelle_phrase(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (un_bloc_ocr_json(texte="Le paragraphe semble incomplet"),),
            (un_bloc_ocr_json(texte="Nouvelle information."),),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Le paragraphe semble incomplet"
    assert blocs_indexables[1].texte == "Nouvelle information."


def test_ne_fusionne_pas_un_paragraphe_continu_apres_une_page_vide(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(
                numero_page=1,
                blocs=(un_bloc_ocr_json(texte="Le paragraphe semble incomplet"),),
            ),
            PageOcr(numero_page=2, blocs=()),
            PageOcr(
                numero_page=3,
                blocs=(un_bloc_ocr_json(texte="est continué ici."),),
            ),
        ),
        nombre_de_pages=3,
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Le paragraphe semble incomplet"
    assert blocs_indexables[1].texte == "est continué ici."


def test_ne_fusionne_pas_deux_paragraphes_distincts_sur_la_meme_page(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(texte="Premier"),
            un_bloc_ocr_json(texte="Deuxième", est_une_continuation=True),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Premier"
    assert blocs_indexables[1].texte == "Deuxième"


def test_ne_fusionne_pas_un_paragraphe_apres_un_titre(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (un_bloc_ocr_json(texte="Début"),),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    texte="Nouvelle section",
                    titre="Nouvelle section",
                    niveau=1,
                ),
                un_bloc_ocr_json(
                    texte="Nouveau contenu",
                    est_une_continuation=True,
                ),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Début"
    assert blocs_indexables[1].texte == "Nouvelle section\nNouveau contenu"


def test_ne_fusionne_pas_un_paragraphe_apres_une_page_vide(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Début"),)),
            PageOcr(
                numero_page=3,
                blocs=(
                    un_bloc_ocr_json(
                        texte="Suite",
                        est_une_continuation=True,
                    ),
                ),
            ),
        ),
        nombre_de_pages=3,
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Début"
    assert blocs_indexables[1].texte == "Suite"


def test_met_a_jour_le_chemin_des_sections_selon_le_niveau_du_titre(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                texte="Section 1",
                titre="Section 1",
                niveau=1,
            ),
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                texte="Section 1.1",
                titre="Section 1.1",
                niveau=2,
            ),
            un_bloc_ocr_json(texte="Contenu"),
        ),)
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[-1]

    assert bloc_indexable.contexte.chemin_des_sections == (
        "Section 1",
        "Section 1.1",
    )


def test_conserve_le_titre_dans_le_premier_bloc_de_la_section(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                texte="Section",
                titre="Section",
                niveau=1,
            ),
            un_bloc_ocr_json(texte="Premier paragraphe"),
            un_bloc_ocr_json(texte="Deuxième paragraphe"),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Section\nPremier paragraphe"
    assert blocs_indexables[1].texte == "Deuxième paragraphe"


def test_deduit_le_niveau_d_un_titre_numerote_meme_si_le_niveau_ocr_est_errone(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    titre = "3.3 Protection des données"
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                titre="3 Recommandations",
                texte="",
                niveau=1,
            ),
            un_bloc_ocr_json(texte="Introduction."),
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                titre=titre,
                texte="",
                niveau=1,
            ),
            un_bloc_ocr_json(texte="Les sauvegardes doivent être protégées."),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    bloc_indexable = blocs_indexables[-1]
    assert bloc_indexable.contexte.chemin_des_sections == (
        "3 Recommandations",
        titre,
    )


def test_cree_un_bloc_autonome_pour_un_titre_sans_contenu(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                texte="Section vide",
                titre="Section vide",
                niveau=1,
            ),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == "Section vide"


def test_conserve_un_titre_place_par_erreur_sur_un_paragraphe(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                titre="6 Fonctionnement d’IPsec",
                texte="",
                niveau=1,
            ),
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.TITRE,
                titre="6.1 Services fournis par IPsec",
                texte="",
                niveau=2,
            ),
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                titre=(
                    "6.1.2 ESP : confidentialité, intégrité et "
                    "authentification des paquets"
                ),
                texte="Le protocole ESP protège les données.",
                niveau=0,
            ),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert blocs_indexables[-1].texte == (
        "6.1.2 ESP : confidentialité, intégrité et authentification des paquets\n"
        "Le protocole ESP protège les données."
    )
    assert blocs_indexables[-1].contexte.chemin_des_sections == (
        "6 Fonctionnement d’IPsec",
        "6.1 Services fournis par IPsec",
        "6.1.2 ESP : confidentialité, intégrité et authentification des paquets",
    )


def test_conserve_les_pages_de_debut_et_de_fin_d_un_bloc(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Début"),)),
            PageOcr(
                numero_page=2,
                blocs=(
                    un_bloc_ocr_json(
                        texte="Fin",
                        est_une_continuation=True,
                    ),
                ),
            ),
        ),
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.page_debut == 1
    assert bloc_indexable.page_fin == 2
    assert bloc_indexable.pages_couvertes == (1, 2)


def test_ne_fusionne_pas_une_recommandation_avec_un_paragraphe(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Contexte"),)),
            PageOcr(
                numero_page=2,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R2",
                        titre="Recommandation",
                        texte="Contenu",
                        est_une_continuation=True,
                    ),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[1].contexte.code_recommandation == "R2"


def test_conserve_une_liste_comme_un_bloc(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.LISTE,
                texte="Premier élément\nDeuxième élément",
                elements_de_liste=("Premier élément", "Deuxième élément"),
            ),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == "Premier élément\nDeuxième élément"
    assert blocs_indexables[0].contexte.type_de_bloc == "liste"


def test_fusionne_deux_parties_de_liste_si_elles_se_suivent(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte="Premier élément",
                ),
            ),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte="Deuxième élément",
                    est_une_continuation=True,
                ),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == "Premier élément\nDeuxième élément"


def test_ne_fusionne_pas_deux_listes_distinctes(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte="Première liste",
                ),
            ),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte="Deuxième liste",
                ),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Première liste"
    assert blocs_indexables[1].texte == "Deuxième liste"


def test_supprime_une_liste_identique_repetee_sur_la_meme_page(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    texte_de_la_liste = "- Première recommandation\n- Deuxième recommandation"
    resultat_ocr = un_resultat_ocr(
        (
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte=texte_de_la_liste,
                ),
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte=texte_de_la_liste,
                ),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == texte_de_la_liste
    assert blocs_indexables[0].pages_couvertes == (1,)


def test_fusionne_la_fin_d_une_puce_avec_le_paragraphe_de_la_page_suivante(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        (
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte="- Attaquant hors ligne : les données sont protégées par",
                ),
            ),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                    texte="exemple en utilisant des fonctions de hachage dédiées.",
                ),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == (
        "- Attaquant hors ligne : les données sont protégées par\n"
        "exemple en utilisant des fonctions de hachage dédiées."
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


def test_ignore_un_pied_de_page(un_bloc_ocr_json, un_resultat_ocr):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(
                type_de_bloc=TypeDeBlocOcr.PIED_DE_PAGE,
                texte="1",
            ),
            un_bloc_ocr_json(texte="Contenu utile"),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == "Contenu utile"


def test_ignore_un_bloc_vide(un_bloc_ocr_json, un_resultat_ocr):
    resultat_ocr = un_resultat_ocr(
        ((
            un_bloc_ocr_json(texte=""),
            un_bloc_ocr_json(texte="Contenu utile"),
        ),)
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == "Contenu utile"


def test_conserve_le_libelle_d_un_titre_numerote(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                        titre="5",
                        texte="Recommandations",
                        niveau=1,
                    ),
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                        titre="5.1",
                        texte="Recommandations générales",
                        niveau=2,
                    ),
                    un_bloc_ocr_json(texte="Contenu de la section"),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "5 Recommandations"
    assert blocs_indexables[1].texte == (
        "5.1 Recommandations générales\nContenu de la section"
    )
    assert blocs_indexables[1].contexte.chemin_des_sections == (
        "5 Recommandations",
        "5.1 Recommandations générales",
    )


def test_conserve_le_paragraphe_associe_a_un_titre_deja_complet(
    un_bloc_ocr_json,
):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                        titre="5.2 Recommandations pour l'entraînement",
                        texte="Le paragraphe qui suit le titre doit être conservé.",
                        niveau=2,
                    ),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == (
        "5.2 Recommandations pour l'entraînement\n"
        "Le paragraphe qui suit le titre doit être conservé."
    )
    assert blocs_indexables[0].contexte.section == (
        "5.2 Recommandations pour l'entraînement"
    )


def test_conserve_les_elements_de_liste_avec_un_texte_d_introduction():
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
        code=None,
        titre=None,
        texte="Introduction de la liste",
        elements_de_liste=("Premier élément", "Deuxième élément"),
    )
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(PageOcr(numero_page=1, blocs=(bloc_ocr,)),),
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == (
        "Introduction de la liste\n- Premier élément\n- Deuxième élément"
    )
    assert bloc_indexable.contexte.type_de_bloc == "liste"


def test_fusionne_un_paragraphe_qui_introduit_une_liste():
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="Les raisons sont les suivantes :",
                    ),
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.LISTE,
                        code=None,
                        titre=None,
                        texte="",
                        elements_de_liste=("Première raison", "Deuxième raison"),
                    ),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == (
        "Les raisons sont les suivantes :\n- Première raison\n- Deuxième raison"
    )
    assert blocs_indexables[0].contexte.type_de_bloc == "liste"
    assert blocs_indexables[0].pages_couvertes == (1,)


def test_conserve_les_elements_de_liste_d_une_recommandation():
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
        code="R2",
        titre="Protéger les données",
        texte="La recommandation contient les actions suivantes :",
        elements_de_liste=("Première action", "Deuxième action"),
    )
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(PageOcr(numero_page=1, blocs=(bloc_ocr,)),),
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == (
        "R2\nProtéger les données\n"
        "La recommandation contient les actions suivantes :\n"
        "- Première action\n- Deuxième action"
    )
    assert bloc_indexable.contexte.type_de_bloc == "recommandation"


def test_conserve_le_texte_et_les_lignes_d_un_tableau():
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.TABLEAU,
        code=None,
        titre=None,
        texte="Titre du tableau",
        lignes_de_tableau=(("Nom", "Valeur"),),
    )
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(PageOcr(numero_page=1, blocs=(bloc_ocr,)),),
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == "Titre du tableau\nNom\tValeur"


def test_fusionne_la_puce_en_debut_de_page_avec_la_liste_precedente():
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="Introduction de la liste",
                        elements_de_liste=("Premier élément",),
                    ),
                ),
            ),
            PageOcr(
                numero_page=2,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="■ Deuxième élément",
                    ),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 1
    assert blocs_indexables[0].texte == (
        "Introduction de la liste\n- Premier élément\n- Deuxième élément"
    )
    assert blocs_indexables[0].pages_couvertes == (1, 2)


def test_ne_fusionne_pas_une_puce_en_debut_de_page_sans_liste_precedente(
    un_bloc_ocr_json,
):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Paragraphe"),)),
            PageOcr(
                numero_page=2,
                blocs=(
                    un_bloc_ocr_json(texte="■ Nouvelle liste"),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Paragraphe"
    assert blocs_indexables[1].texte == "- Nouvelle liste"
