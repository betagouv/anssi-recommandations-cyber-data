import json
from typing import Any, Iterator, Optional

from docling_core.transforms.chunker import BaseChunker, BaseChunk, DocMeta
from docling_core.types import DoclingDocument as DLDocument
from docling_core.types.doc import DocItem, DocItemLabel, ProvenanceItem
from docling_core.types.doc.base import BoundingBox
from pydantic import Field

from guides.indexeur import DocumentPDF
from guides.indexeur_docling import IndexeurDocling, ChunkerDocling


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


def test_peut_indexer_un_document_pdf(
    mock_post_session_creation_document, une_reponse_document, fichier_pdf
):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    indexeur = IndexeurDocling("http://albert.local", ChunkerDeTest())
    mock_post_session_creation_document(indexeur.session, une_reponse_document)

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert reponses[0].name == "test.pdf"
    assert reponses[0].collection_id == "12345"


def test_le_payload_est_passe_en_argument(
    mock_post_session_creation_document, une_reponse_document, fichier_pdf
):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    chunker = ChunkerDeTest().avec_base_chunker(
        BaseChunkerDeTest().avec_base_chunk(
            ConstructeurDeBaseChunk().avec_numero_page(10).construis()
        )
    )
    indexeur = IndexeurDocling("http://albert.local", chunker)
    mock_post_session_creation_document(indexeur.session, une_reponse_document)

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    indexeur.ajoute_documents([document], "12345")

    [args, kwargs] = indexeur.session.post._mock_call_args
    assert kwargs["data"] is not None
    assert kwargs["data"]["collection"] == "12345"
    assert kwargs["data"]["chunker"] == "NoSplitter"
    metadata = json.loads(kwargs["data"]["metadata"])
    assert metadata["page"] == 10


def test_ne_cree_pas_de_document_si_le_paragraphe_est_trop_court(
    mock_post_session_creation_document, une_reponse_document, fichier_pdf
):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    chunker = ChunkerDeTest().avec_base_chunker(
        BaseChunkerDeTest().avec_base_chunk(
            ConstructeurDeBaseChunk().avec_paragraphe("1").construis()
        )
    )
    indexeur = IndexeurDocling("http://albert.local", chunker)
    mock_post_session_creation_document(indexeur.session, une_reponse_document)

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 0
