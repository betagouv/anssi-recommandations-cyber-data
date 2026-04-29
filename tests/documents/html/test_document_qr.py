from documents.html.document_html import BlocPageReponse, GenerateurReponsesMaitrisees


def test_generateur_qr_cree_des_blocs_avec_question_id_reponse_et_reponse(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    generateur = GenerateurReponsesMaitrisees()
    pages = generateur.genere(
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_texte("Qui est le directeur de l'ANSSI ?")
            .ayant_les_enfants(["enf/1"])
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Vincent Strubel.")
            .portant_la_reference("enf/1")
            .construis(),
        ],
        resultat_conversion.document,
    )

    assert len(pages) == 1
    bloc = pages[0].blocs[0]
    assert isinstance(bloc, BlocPageReponse)
    assert bloc.texte == "Qui est le directeur de l'ANSSI ?"
    assert bloc.id_reponse == "qui-est-le-directeur-de-lanssi"
    assert bloc.reponse == "Vincent Strubel."
