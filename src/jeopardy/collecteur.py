from dataclasses import dataclass
from itertools import islice
from typing import NamedTuple, TypedDict, Generator

from documents.docling.multi_processeur import Multiprocesseur
from evenement.bus import BusEvenement
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
)
from jeopardy.evenements import (
    CorpsEvenementQuestionsGenereesEnErreur,
    EvenementQuestionsGenereesEnErreur,
)
from jeopardy.questions import (
    EntrepotQuestionGeneree,
    QuestionGeneree,
    GenerationQuestionEnErreur,
)


class ChunkSource(TypedDict):
    id: int
    contenu: str
    page: int


class Chunk(NamedTuple):
    contenu: str
    id: int
    page: int


class Document:
    def __init__(self, data: dict[str, dict[str, str | list[ChunkSource]]]):
        self.nom_document = list(data.keys())[0]
        document_data = data[self.nom_document]
        id_document = document_data["id"]
        if isinstance(id_document, str):
            self.id_document: str = id_document
        chunks = document_data["chunks"]
        if isinstance(chunks, list):
            self.chunks: list[Chunk] = list(
                map(
                    lambda c: Chunk(contenu=c["contenu"], id=c["id"], page=c["page"]),
                    chunks,
                )
            )


@dataclass
class ChunksAAjouter:
    chunks: list[Chunk]
    id_document: str


class CollecteurDeQuestions:
    def __init__(
        self,
        client_albert: ClientAlbertJeopardy,
        prompt: str,
        entrepot_questions_generees: EntrepotQuestionGeneree,
        bus_evenement: BusEvenement,
        multi_processeur: Multiprocesseur = Multiprocesseur(5),
    ):
        super().__init__()
        self.client_albert = client_albert
        self.prompt = prompt
        self.entrepot_questions_generees = entrepot_questions_generees
        self.bus_evenement = bus_evenement
        self.multi_processeur = multi_processeur

    def collecte(
        self,
        document: Document,
    ):
        def decoupe_la_liste_de_documents(
            iterable: list[Chunk],
        ) -> Generator[ChunksAAjouter, None, None]:
            it = iter(iterable)
            i = 0
            while True:
                sous_ensemble = list(islice(it, 10))
                if not sous_ensemble:
                    break
                yield ChunksAAjouter(
                    chunks=sous_ensemble, id_document=document.id_document
                )
                i = i + 1

        resultats = self.multi_processeur.execute(
            self._genere_questions,
            decoupe_la_liste_de_documents(document.chunks),
        )
        contient_des_erreurs: list[GenerationQuestionEnErreur] = list(
            filter(lambda x: isinstance(x, GenerationQuestionEnErreur), resultats)
        )
        if len(contient_des_erreurs) == 0:
            questions_generees = [q for qs in resultats for q in qs]
            [self.entrepot_questions_generees.persiste(q) for q in questions_generees]

    def _genere_questions(
        self, chunks_a_ajouter: ChunksAAjouter
    ) -> list[QuestionGeneree] | GenerationQuestionEnErreur:
        questions_generees = []
        try:
            for chunk in chunks_a_ajouter.chunks:
                liste_questions = self.client_albert.genere_questions(
                    self.prompt, chunk.contenu
                )
                for question in liste_questions:
                    questions_generees.append(
                        QuestionGeneree(
                            contenu=question,
                            contenu_origine=chunk.contenu,
                            id_document=chunks_a_ajouter.id_document,
                            id_chunk=chunk.id,
                            page=chunk.page,
                        )
                    )
        except Exception as e:
            self.bus_evenement.publie(
                EvenementQuestionsGenereesEnErreur(
                    corps=CorpsEvenementQuestionsGenereesEnErreur(
                        id_document=chunks_a_ajouter.id_document, erreur=str(e)
                    )
                )
            )
            return GenerationQuestionEnErreur()
        return questions_generees
