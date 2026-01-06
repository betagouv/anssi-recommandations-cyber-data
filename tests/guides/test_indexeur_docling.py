import json
from typing import Any, Iterator, Optional, Union
from unittest.mock import Mock

from docling_core.transforms.chunker import BaseChunker, BaseChunk, DocMeta
from docling_core.types import DoclingDocument as DLDocument
from docling_core.types.doc import DocItem, DocItemLabel, ProvenanceItem
from docling_core.types.doc.base import BoundingBox
from pydantic import Field
from requests.models import Response

from guides.executeur_requete import ExecuteurDeRequete
from guides.indexeur import (
    DocumentPDF,
    ReponseDocumentEnSucces,
    ReponseDocumentEnErreur,
    ReponseDocument,
)
from guides.indexeur_docling import IndexeurDocling, ChunkerDocling
from guides.multi_processeur import Multiprocesseur


class ConstructeurDeBaseChunk:
    def __init__(self):
        super().__init__()
        self.texte = "Un texte chunké"
        self.numero_page = 5

    def avec_numero_page(self, numero_page: int):
        self.numero_page = numero_page
        return self

    def avec_paragraphe(self, paragraphe: str):
        self.texte = paragraphe
        return self

    def construis(self) -> BaseChunk:
        return BaseChunk(
            text=self.texte,
            meta=DocMeta(
                doc_items=[
                    DocItem(
                        prov=[
                            ProvenanceItem(
                                page_no=self.numero_page,
                                bbox=BoundingBox(l=0.0, b=0.0, r=0.0, t=0.0),
                                charspan=(0, 0),
                            ),
                        ],
                        label=DocItemLabel.TEXT,
                        self_ref="#/tables/9",
                    )
                ]
            ),
        )


class BaseChunkerDeTest(BaseChunker):
    base_chunk: Optional[BaseChunk] = Field(default=None)

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.base_chunk = ConstructeurDeBaseChunk().construis()

    def avec_base_chunk(self, base_chunk: BaseChunk):
        self.base_chunk = base_chunk
        return self

    def chunk(self, dl_doc: DLDocument, **kwargs: Any) -> Iterator[BaseChunk]:
        if self.base_chunk is not None:
            yield self.base_chunk


class ChunkerDeTest(ChunkerDocling):
    def __init__(self):
        super().__init__()
        self.chunker = BaseChunkerDeTest()

    def applique(self, document: DocumentPDF) -> list[BaseChunk]:
        return list(self.chunker.chunk(DLDocument(name=document.chemin_pdf)))

    def avec_base_chunker(self, chunker: BaseChunker):
        self.chunker = chunker
        return self


class ReponseAttendueAbstraite:
    def __init__(self, reponse: ReponseDocument):
        super().__init__()
        self.reponse_document = reponse


class ReponseAttendueOK(ReponseAttendueAbstraite):
    def __init__(self, reponse: ReponseDocumentEnSucces):
        super().__init__(reponse)

    @property
    def status_code(self) -> int:
        return 201

    @property
    def reponse(self) -> dict:
        return self.reponse_document._asdict()


class ReponseAttendueKO(ReponseAttendueAbstraite):
    def __init__(
        self, reponse: ReponseDocumentEnErreur, leve_une_erreur: str | None = None
    ):
        super().__init__(reponse)
        self.leve_une_erreur = leve_une_erreur

    @property
    def status_code(self) -> int:
        return 400

    @property
    def reponse(self) -> dict:
        if self.leve_une_erreur is not None:
            raise RuntimeError(self.leve_une_erreur)
        return self.reponse_document._asdict()


ReponseAttendue = Union[ReponseAttendueOK, ReponseAttendueKO]


class ExecuteurDeRequeteDeTest(ExecuteurDeRequete):
    def __init__(self, reponse_attendue: list[ReponseAttendue]):
        super().__init__()
        self.reponse_attendue = reponse_attendue
        self.payload_recu: None | dict = None
        self.index_courant = 0

    def initialise(self, clef_api: str):
        pass

    def poste(self, url: str, payload: dict, fichiers: Optional[dict]) -> Response:
        reponse = Mock()
        reponse.status_code = self.reponse_attendue[self.index_courant].status_code
        reponse.json.return_value = self.reponse_attendue[self.index_courant].reponse
        self.payload_recu = payload
        self.index_courant += 1
        return reponse


class MultiProcesseurDeTest(Multiprocesseur):
    def execute(self, func, iterable) -> list:
        resultats = []
        for chunk in iterable:
            resultats.append(func(chunk))
        return resultats


def test_peut_indexer_un_document_pdf(une_reponse_document, fichier_pdf):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    executeur_de_requete = ExecuteurDeRequeteDeTest(
        [ReponseAttendueOK(une_reponse_document)]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        ChunkerDeTest(),
        executeur_de_requete,
        multi_processeur,
    )

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert reponses[0].name == "test.pdf"
    assert reponses[0].collection_id == "12345"


def test_peut_indexer_plusieurs_documents_pdf(
    une_reponse_document_parametree, fichier_pdf
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_1.pdf").resolve())
    executeur_de_requete = ExecuteurDeRequeteDeTest(
        [
            ReponseAttendueOK(une_reponse_document_parametree("1", "document_1.pdf")),
            ReponseAttendueOK(une_reponse_document_parametree("2", "document_2.pdf")),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        ChunkerDeTest(),
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


def test_le_payload_est_passe_en_argument(une_reponse_document, fichier_pdf):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    executeur_de_requete = ExecuteurDeRequeteDeTest(
        [ReponseAttendueOK(une_reponse_document)]
    )
    multi_processeur = MultiProcesseurDeTest()
    chunker = ChunkerDeTest().avec_base_chunker(
        BaseChunkerDeTest().avec_base_chunk(
            ConstructeurDeBaseChunk().avec_numero_page(10).construis()
        )
    )
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        chunker,
        executeur_de_requete,
        multi_processeur,
    )

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    indexeur.ajoute_documents([document], "12345")

    assert executeur_de_requete.payload_recu is not None
    assert executeur_de_requete.payload_recu["collection"] == "12345"
    assert executeur_de_requete.payload_recu["chunker"] == "NoSplitter"
    metadata = json.loads(executeur_de_requete.payload_recu["metadata"])
    assert metadata["page"] == 10


def test_ne_cree_pas_de_document_si_le_paragraphe_est_trop_court(
    une_reponse_document, fichier_pdf
):
    executeur_de_requete = ExecuteurDeRequeteDeTest(
        [ReponseAttendueOK(une_reponse_document)]
    )
    multi_processeur = MultiProcesseurDeTest()
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    chunker = ChunkerDeTest().avec_base_chunker(
        BaseChunkerDeTest().avec_base_chunk(
            ConstructeurDeBaseChunk().avec_paragraphe("1").construis()
        )
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
    une_reponse_document_parametree, fichier_pdf
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_2.pdf").resolve())
    executeur_de_requete = ExecuteurDeRequeteDeTest(
        [
            ReponseAttendueOK(une_reponse_document_parametree("1", "document_1.pdf")),
            ReponseAttendueKO(ReponseDocumentEnErreur("Une erreur", "document_2.pdf")),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        ChunkerDeTest(),
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


def test_continue_l_indexation_si_un_document_n_est_pas_indexe_et_qu_une_erreur_est_levee(
    une_reponse_document_parametree, fichier_pdf
):
    document_1 = str(fichier_pdf("document_1.pdf").resolve())
    document_2 = str(fichier_pdf("document_2.pdf").resolve())
    executeur_de_requete = ExecuteurDeRequeteDeTest(
        [
            ReponseAttendueOK(une_reponse_document_parametree("1", "document_1.pdf")),
            ReponseAttendueKO(
                ReponseDocumentEnErreur("Une erreur", "document_2.pdf"),
                "Erreur de traitement",
            ),
        ]
    )
    multi_processeur = MultiProcesseurDeTest()
    indexeur = IndexeurDocling(
        "http://albert.local",
        "une_clef",
        ChunkerDeTest(),
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
    assert reponses[1].detail == "Erreur de traitement"
    assert reponses[1].document_en_erreur == "document_2.pdf"
