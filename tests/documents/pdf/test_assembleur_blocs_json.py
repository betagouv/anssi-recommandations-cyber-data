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

    assert bloc_indexable.texte == "Le système doit être protégé."
    assert bloc_indexable.contexte.type_de_bloc == "recommandation"
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
