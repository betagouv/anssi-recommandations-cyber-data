import pytest

from configuration import recupere_configuration
from documents.ajoute_document_a_la_collection import collecte_guide_anssi
from documents.pdf.document_pdf import DocumentPDF


def test_collecte_guide_anssi_retourne_un_document(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve() / "test.pdf")

    document = collecte_guide_anssi(chemin_fichier)
    print(document)
    assert isinstance(document, DocumentPDF)
    assert document.chemin_pdf == chemin_fichier
    assert (
            document.url_pdf
            == "https://messervices.cyber.gouv.fr/documents-guides/test.pdf"
    )

@pytest.mark.skip(
    reason="En attendant d’exposer une fonction spécifique pour les documents distants"
)
def test_collecte_guide_anssi_utilise_url_specifique_depuis_json(
        dossier_guide_anssi,
        fichier_urls_specifiques,
):
    chemin_fichier = str(dossier_guide_anssi.resolve() / "test.pdf")

    document = collecte_guide_anssi(
        path=chemin_fichier,
        configuration_msc=recupere_configuration().msc,
        path_url=str(fichier_urls_specifiques),
    )

    assert document.url_pdf == "https://url_de_test.com"