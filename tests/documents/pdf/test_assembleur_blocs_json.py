from documents.pdf.assembleur_blocs_json import (
    AssembleurDeBlocsJson,
    BlocOcr,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)


def test_conserve_les_blocs_distincts_d_une_meme_page(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    un_bloc_ocr_json(texte="Premier paragraphe"),
                    un_bloc_ocr_json(texte="Deuxième paragraphe"),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Premier paragraphe"
    assert blocs_indexables[1].texte == "Deuxième paragraphe"


def test_conserve_l_ordre_des_blocs_d_une_page(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    un_bloc_ocr_json(texte="Premier"),
                    un_bloc_ocr_json(texte="Deuxième"),
                    un_bloc_ocr_json(texte="Troisième"),
                ),
            ),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 3
    assert blocs_indexables[0].texte == "Premier"
    assert blocs_indexables[1].texte == "Deuxième"
    assert blocs_indexables[2].texte == "Troisième"


def test_cree_un_bloc_indexable_avec_son_type_son_code_et_son_titre():
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
        code="R24",
        titre="Protéger le système",
        texte="Le système doit être protégé.",
    )
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(PageOcr(numero_page=1, blocs=(bloc_ocr,)),),
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == (
        "R24\nProtéger le système\nLe système doit être protégé."
    )
    assert bloc_indexable.contexte.type_de_bloc == "recommendation"
    assert bloc_indexable.contexte.code_recommandation == "R24"
    assert bloc_indexable.contexte.titre == "Protéger le système"


def test_conserve_les_pages_couvertes_par_un_bloc(un_bloc_ocr_json):
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=3,
        pages=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Page 1"),)),
            PageOcr(numero_page=3, blocs=(un_bloc_ocr_json(texte="Page 3"),)),
        ),
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].page_debut == 1
    assert blocs_indexables[0].page_fin == 1
    assert blocs_indexables[0].pages_couvertes == (1,)
    assert blocs_indexables[1].page_debut == 3
    assert blocs_indexables[1].page_fin == 3
    assert blocs_indexables[1].pages_couvertes == (3,)


def test_met_a_jour_le_chemin_des_sections_selon_le_niveau_du_titre(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (un_bloc_ocr_json(type_de_bloc=TypeDeBlocOcr.TITRE, titre="1", texte=""),),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="1.1 Introduction",
                    texte="",
                ),
                un_bloc_ocr_json(texte="Contenu"),
            ),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].contexte.chemin_des_sections == ("1",)
    assert blocs_indexables[1].contexte.chemin_des_sections == (
        "1",
        "1.1 Introduction",
    )


def test_conserve_le_titre_dans_le_premier_bloc_de_la_section(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="6.1 Services fournis",
                    texte="",
                ),
                un_bloc_ocr_json(texte="Le service est décrit ici."),
            ),
        )
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == "6.1 Services fournis\nLe service est décrit ici."
    assert bloc_indexable.contexte.titre == "6.1 Services fournis"
    assert bloc_indexable.contexte.niveau is None


def test_cree_un_bloc_autonome_pour_un_titre_sans_contenu(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="6 Fonctionnement d’IPsec",
                    texte="",
                ),
            ),
        )
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == "6 Fonctionnement d’IPsec"
    assert bloc_indexable.contexte.type_de_bloc == "heading"
    assert bloc_indexable.contexte.niveau == 1


def test_conserve_un_titre_place_par_erreur_sur_un_paragraphe(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                    titre="6.1.2 ESP",
                    texte="Le protocole ESP est décrit ici.",
                ),
            ),
        )
    )

    bloc_indexable = AssembleurDeBlocsJson().assemble(resultat_ocr)[0]

    assert bloc_indexable.texte == "6.1.2 ESP\nLe protocole ESP est décrit ici."
    assert bloc_indexable.contexte.type_de_bloc == "paragraph"
    assert bloc_indexable.contexte.titre == "6.1.2 ESP"
    assert bloc_indexable.contexte.niveau is None


def test_fusionne_un_paragraphe_qui_continue_sur_la_page_suivante(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (un_bloc_ocr_json(texte="Début"),),
            (un_bloc_ocr_json(texte="Suite", est_une_continuation=True),),
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
        blocs_par_page=(
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


def test_ne_fusionne_pas_un_paragraphe_apres_une_phrase_terminee(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
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
        blocs_par_page=(
            (un_bloc_ocr_json(texte="Le paragraphe semble incomplet"),),
            (un_bloc_ocr_json(texte="Nouvelle information."),),
        )
    )

    blocs_indexables = AssembleurDeBlocsJson().assemble(resultat_ocr)

    assert len(blocs_indexables) == 2
    assert blocs_indexables[0].texte == "Le paragraphe semble incomplet"
    assert blocs_indexables[1].texte == "Nouvelle information."


def test_ne_fusionne_pas_un_paragraphe_apres_une_page_vide(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(numero_page=1, blocs=(un_bloc_ocr_json(texte="Début"),)),
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
    assert blocs_indexables[0].texte == "Début"
    assert blocs_indexables[1].texte == "est continué ici."


def test_ne_fusionne_pas_deux_paragraphes_distincts_sur_la_meme_page(
    un_bloc_ocr_json,
    un_resultat_ocr,
):
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(texte="Premier"),
                un_bloc_ocr_json(texte="Deuxième", est_une_continuation=True),
            ),
        )
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
        blocs_par_page=(
            (un_bloc_ocr_json(texte="Début"),),
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="Nouvelle section",
                    texte="Nouvelle section",
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


def test_ne_fusionne_pas_un_paragraphe_apres_une_page_non_contigue(
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
