import json

from documents.docling.multi_processeur import Multiprocesseur
from documents.indexeur.indexeur import ReponseDocumentEnErreur
from documents.indexeur.indexeur_docling import IndexeurDocling
from documents.pdf.document_pdf import DocumentPDF


class MultiProcesseurDeTest(Multiprocesseur):
    def execute(self, func, iterable) -> list:
        resultats = []
        for chunk in iterable:
            resultats.append(func(chunk))
        return resultats


def test_peut_indexer_un_document_pdf(
    une_reponse_document,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_OK,
    une_reponse_chunk,
    un_chunker_avec_generation_de_page_statique,
):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(une_reponse_document),
            une_reponse_attendue_OK(une_reponse_chunk),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        un_chunker_avec_generation_de_page_statique().construis(),
        executeur_de_requete,
        multi_processeur,
    )

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert reponses[0].name == "test.pdf"
    assert reponses[0].collection_id == "12345"


def test_peut_indexer_un_document_puis_ajouter_un_chunk(
    une_reponse_document,
    une_reponse_chunk,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_OK,
    un_chunker_avec_generation_de_page_statique,
):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(une_reponse_document),
            une_reponse_attendue_OK(une_reponse_chunk),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        un_chunker_avec_generation_de_page_statique().a_la_page(10).construis(),
        executeur_de_requete,
        multi_processeur,
    )

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 1
    url_appelee = "http://albert.local/documents/doc123/chunks"
    assert executeur_de_requete.payload_recu[url_appelee] is not None
    assert len(executeur_de_requete.payload_recu[url_appelee]["chunks"]) == 1
    chunks = executeur_de_requete.payload_recu[url_appelee]["chunks"]
    assert chunks[0]["content"] == "Un contenu"
    assert chunks[0]["metadata"] == {
        "source_url": "https://example.com/test.pdf",
        "page": 10,
        "nom_document": "test.pdf",
    }


def test_peut_indexer_plusieurs_documents(
    une_reponse_document_parametree,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_OK,
    une_reponse_chunk,
    un_chunker_avec_generation_de_page_statique,
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_1.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(
                une_reponse_document_parametree("1", "document_1.pdf")
            ),
            une_reponse_attendue_OK(une_reponse_chunk),
            une_reponse_attendue_OK(
                une_reponse_document_parametree("2", "document_2.pdf")
            ),
            une_reponse_attendue_OK(une_reponse_chunk),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        un_chunker_avec_generation_de_page_statique().construis(),
        executeur_de_requete,
        multi_processeur,
    )

    reponses = indexeur.ajoute_documents(
        [
            (DocumentPDF(document_1, "https://example.com/document_1.pdf")),
            DocumentPDF(document_2, "https://example.com/document_2.pdf"),
        ],
        "12345",
    )

    assert len(reponses) == 2
    assert reponses[0].id == "1"
    assert reponses[0].name == "document_1.pdf"
    assert reponses[0].collection_id == "12345"
    assert reponses[1].id == "2"
    assert reponses[1].name == "document_2.pdf"
    assert reponses[1].collection_id == "12345"


def test_les_informations_de_creation_de_document_sont_passees_a_la_requete(
    une_reponse_document,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_OK,
    un_chunker_avec_generation_de_page_statique,
):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [une_reponse_attendue_OK(une_reponse_document)]
    )
    multi_processeur = MultiProcesseurDeTest()
    chunker = un_chunker_avec_generation_de_page_statique().a_la_page(10).construis()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        chunker,
        executeur_de_requete,
        multi_processeur,
    )

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    indexeur.ajoute_documents([document], "12345")

    url_appelee = "http://albert.local/documents"
    assert executeur_de_requete.payload_recu[url_appelee] is not None
    assert executeur_de_requete.payload_recu[url_appelee]["collection_id"] == 12345
    assert executeur_de_requete.payload_recu[url_appelee]["chunker"] == "NoSplitter"
    metadata = json.loads(executeur_de_requete.payload_recu[url_appelee]["metadata"])
    assert metadata == {
        "source_url": "https://example.com/test.pdf",
        "nom_document": "test.pdf",
    }


def test_ne_cree_pas_de_document_si_le_paragraphe_est_trop_court(
    une_reponse_document,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_OK,
    un_chunker_avec_generation_de_page_statique,
):
    executeur_de_requete = un_executeur_de_requete(
        [une_reponse_attendue_OK(une_reponse_document)]
    )
    multi_processeur = MultiProcesseurDeTest()
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    chunker = (
        un_chunker_avec_generation_de_page_statique().avec_le_contenu("1").construis()
    )
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        chunker,
        executeur_de_requete,
        multi_processeur,
    )

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 0


def test_continue_l_indexation_si_un_document_n_est_pas_indexe(
    une_reponse_document_parametree,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_OK,
    une_reponse_attendue_KO,
    une_reponse_chunk,
    un_chunker_avec_generation_de_page_statique,
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_2.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(
                une_reponse_document_parametree("1", "document_1.pdf")
            ),
            une_reponse_attendue_OK(une_reponse_chunk),
            une_reponse_attendue_KO(
                ReponseDocumentEnErreur("Une erreur", "document_2.pdf")
            ),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        un_chunker_avec_generation_de_page_statique().construis(),
        executeur_de_requete,
        multi_processeur,
    )

    reponses = indexeur.ajoute_documents(
        [
            (DocumentPDF(document_1, "https://example.com/document_1.pdf")),
            DocumentPDF(document_2, "https://example.com/document_2.pdf"),
        ],
        "12345",
    )

    assert len(reponses) == 2
    assert reponses[0].id == "1"
    assert reponses[1].detail == "Une erreur"
    assert reponses[1].document_en_erreur == "document_2.pdf"


def test_continue_l_indexation_si_un_chunk_n_est_pas_ajoute_a_un_document_suite_a_une_erreur(
    une_reponse_document_parametree,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_KO,
    une_reponse_attendue_OK,
    une_reponse_chunk,
    une_reponse_chunk_en_erreur,
    un_chunker_avec_generation_de_page_statique,
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_2.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(
                une_reponse_document_parametree("1", "document_1.pdf")
            ),
            une_reponse_attendue_OK(une_reponse_chunk),
            une_reponse_attendue_OK(
                une_reponse_document_parametree("2", "document_2.pdf")
            ),
            une_reponse_attendue_KO(une_reponse_chunk_en_erreur),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        un_chunker_avec_generation_de_page_statique().construis(),
        executeur_de_requete,
        multi_processeur,
    )

    reponses = indexeur.ajoute_documents(
        [
            (DocumentPDF(document_1, "https://example.com/document_1.pdf")),
            DocumentPDF(document_2, "https://example.com/document_2.pdf"),
        ],
        "12345",
    )

    assert len(reponses) == 2
    assert reponses[0].id == "1"
    assert "Erreur de traitement" in reponses[1].detail
    assert reponses[1].document_en_erreur == "document_2.pdf"


def test_continue_l_indexation_si_un_document_n_est_pas_indexe_suite_a_une_erreur(
    une_reponse_document_parametree,
    fichier_pdf,
    un_executeur_de_requete,
    une_reponse_attendue_KO,
    une_reponse_attendue_OK,
    une_reponse_chunk,
    une_reponse_chunk_en_erreur,
    un_chunker_avec_generation_de_page_statique,
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_2.pdf").resolve())
    executeur_de_requete = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(
                une_reponse_document_parametree("1", "document_1.pdf")
            ),
            une_reponse_attendue_OK(une_reponse_chunk),
            une_reponse_attendue_OK(
                une_reponse_document_parametree("2", "document_2.pdf")
            ),
            une_reponse_attendue_KO(une_reponse_chunk_en_erreur, "Erreur JSON"),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        un_chunker_avec_generation_de_page_statique().construis(),
        executeur_de_requete,
        multi_processeur,
    )

    reponses = indexeur.ajoute_documents(
        [
            (DocumentPDF(document_1, "https://example.com/document_1.pdf")),
            DocumentPDF(document_2, "https://example.com/document_2.pdf"),
        ],
        "12345",
    )

    assert len(reponses) == 2
    assert reponses[0].id == "1"
    assert "Erreur JSON" in reponses[1].detail
    assert reponses[1].document_en_erreur == "document_2.pdf"
