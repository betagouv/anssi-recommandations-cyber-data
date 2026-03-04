import glob

from configuration import MSC, recupere_configuration
from documents.pdf.cree_document_pdf import cree_document_pdf
from documents.pdf.document_pdf import DocumentPDF


def collecte_guides_anssi(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> list[DocumentPDF]:
    chemins = glob.glob(f"{dossier}/*.pdf")
    return [cree_document_pdf(chemin, configuration_msc) for chemin in chemins]


def collecte_guide_anssi(
    path: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> DocumentPDF:
    return cree_document_pdf(path, configuration_msc)
