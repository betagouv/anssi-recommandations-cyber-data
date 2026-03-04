import pytest

from configuration import recupere_configuration
from documents.pdf.cree_document_pdf import cree_document_pdf


@pytest.mark.skip(
    reason="En attendant d’exposer une fonction spécifique pour les documents distants"
)
def test_cree_document_pdf_via_un_fichier(
    dossier_guide_anssi, fichier_urls_specifiques
):
    chemin_fichier = str(dossier_guide_anssi.resolve() / "test.pdf")
    configuration_msc = recupere_configuration().msc

    document = cree_document_pdf(
        chemin_fichier, configuration_msc, str(fichier_urls_specifiques)
    )

    assert document.url_pdf == "https://url_de_test.com"


@pytest.mark.skip(
    reason="Ne fonctionne pas pour le moment car dépend du chemin fourni en paramètre, hors on ne connait pas les chemins détenus dans le fichier json"
)
def test_cree_document_pdf_via_un_fichier_en_ne_prenant_que_les_pdf(
    dossier_guide_anssi, fichier_urls_specifiques
):
    chemin_fichier = str(dossier_guide_anssi.resolve() / "test.pdf")
    configuration_msc = recupere_configuration().msc

    document = cree_document_pdf(
        chemin_fichier, configuration_msc, str(fichier_urls_specifiques)
    )

    assert document.url_pdf == "https://url_de_test.com"
