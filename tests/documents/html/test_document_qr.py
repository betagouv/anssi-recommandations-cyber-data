import json

from documents.collecte.collecte import collecte_document_maitrise
from documents.html.document_html import BlocPageReponse, GenerateurReponsesMaitrisees


def test_generateur_qr_cree_des_blocs_avec_question_et_id_reponse(
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


def test_generateur_qr_ecrit_le_fichier_de_mapping(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
    tmp_path,
):
    chemin_html = tmp_path / "faq.html"
    chemin_html.touch()

    document = collecte_document_maitrise(chemin_html)

    document.generateur.genere(
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

    mapping_path = tmp_path / "faq.mapping.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    assert mapping_path.exists()
    assert mapping["qui-est-le-directeur-de-lanssi"] == "Vincent Strubel."
