from dataclasses import dataclass

from guides.chunker_docling import TypeFichier
from guides.guide import Guide, Position
from guides.indexeur import DocumentPDF, ReponseDocumentEnSucces
from guides.indexeur_docling import IndexeurDocling


class MultiprocesseurSequentiel:
    def execute(self, func, iterable):
        return [func(x) for x in iterable]


@dataclass
class ChunkerDoclingDeTest:
    nom_fichier: str = "bloc.txt"
    type_fichier: TypeFichier = TypeFichier.TEXTE

    def applique(self, document: DocumentPDF) -> Guide:
        guide = Guide(document)
        guide.ajoute_bloc_a_la_page(
            numero_page=1,
            position=Position(x=0, y=0, largeur=1, hauteur=1),
            texte="PARAGRAPHE_SOURCE",
        )
        return guide


def test_indexeur_docling_indexe_une_liste_de_questions_par_bloc(
    un_executeur_de_requete,
    une_reponse_attendue_OK,
):
    executeur = un_executeur_de_requete(
        [
            une_reponse_attendue_OK(ReponseDocumentEnSucces("1", "doc", "col", "", "")),
            une_reponse_attendue_OK(ReponseDocumentEnSucces("2", "doc", "col", "", "")),
        ]
    )

    def producteur(_texte: str) -> list[str]:
        return ["question 1 ?", "question 2 ?"]

    indexeur = IndexeurDocling(
        url="http://albert.local",
        clef_api="clef",
        chunker=ChunkerDoclingDeTest(),
        executeur_de_requete=executeur,
        multi_processeur=MultiprocesseurSequentiel(),
        producteur_contenus=producteur,
    )

    reponses = indexeur.ajoute_documents(
        documents=[DocumentPDF(chemin_pdf="/tmp/a.pdf", url_pdf="http://x")],
        id_collection="col",
    )

    fichier_poste = executeur.fichiers_recus["file"][1]

    assert len(reponses) == 2
    assert all(isinstance(r, ReponseDocumentEnSucces) for r in reponses)
    assert fichier_poste == "question 2 ?".encode("utf-8")
