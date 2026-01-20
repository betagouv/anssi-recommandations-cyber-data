from guides.chunker_docling import TypeFichier
from guides.chunker_docling_hierarchique import ChunkerDoclingHierarchique
from guides.indexeur import DocumentPDF


def test_le_guide_retourne_le_nom_du_document(
    fichier_pdf, un_convertisseur_avec_un_texte
):
    chemin_fichier_de_test = str(fichier_pdf("document_hierarchique.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    guide = ChunkerDoclingHierarchique(un_convertisseur_avec_un_texte()).applique(
        document=document
    )

    assert guide.nom_document == "document_hierarchique.pdf"


def test_retourne_le_nom_du_fichier(fichier_pdf, un_convertisseur_avec_un_texte):
    chemin_fichier_de_test = str(fichier_pdf("document_hierarchique.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    chunker = ChunkerDoclingHierarchique(un_convertisseur_avec_un_texte())
    chunker.applique(document=document)

    assert chunker.nom_fichier == "document_hierarchique.pdf"


def test_retourne_le_type_du_fichier():
    chunker = ChunkerDoclingHierarchique()

    assert chunker.type_fichier == TypeFichier.PDF
