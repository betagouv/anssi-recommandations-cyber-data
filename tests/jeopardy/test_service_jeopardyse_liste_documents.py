from jeopardy.client_albert_jeopardy import ReponseDocumentOrigine
from jeopardy.service import ListeDeDocuments
from jeopardy.service_jeopardyse_liste_de_documents import ServiceJeopardyseDocuments


def test_recupere_un_document_source_depuis_son_identifiant(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
    un_bus_d_evenement,
):
    id_collection = "collection-123"
    nom_document = "anssi-guide-1"

    client_albert = un_client_albert_de_test().qui_retourne_une_liste_de_documents_lors_de_la_recherche_par_noms(
        [("123456789", nom_document, 2)]
    )

    ServiceJeopardyseDocuments(
        client_albert,
        un_entrepot_memoire,
        un_bus_d_evenement,
        "Prompt",
        un_multiprocesseur,
    ).recupere_les_documents(
        ListeDeDocuments(id_collection=id_collection, noms_documents=[nom_document]),
    )

    assert client_albert.noms_documents_recuperes == [nom_document]
    assert client_albert.identifiant_collection_lu == id_collection


def test_retourne_les_documents_recherches(
    un_client_albert_de_test,
    un_entrepot_memoire,
    un_multiprocesseur,
    un_bus_d_evenement,
):
    id_collection = "collection-123"
    client_albert = un_client_albert_de_test().qui_retourne_une_liste_de_documents_lors_de_la_recherche_par_noms(
        [("doc-123", "anssi-guide-1", 5), ("doc-456", "anssi-guide-2", 3)]
    )

    documents, identifiant_collection = ServiceJeopardyseDocuments(
        client_albert,
        un_entrepot_memoire,
        un_bus_d_evenement,
        "Prompt",
        un_multiprocesseur,
    ).recupere_les_documents(
        ListeDeDocuments(id_collection=id_collection, noms_documents=["anssi-guide-1"])
    )

    assert identifiant_collection == id_collection
    assert len(documents) == 2
    assert documents == [
        ReponseDocumentOrigine(id="doc-123", nom="anssi-guide-1", nombre_chunks=5),
        ReponseDocumentOrigine(id="doc-456", nom="anssi-guide-2", nombre_chunks=3),
    ]
