import json

from documents.indexe_documents_rag import ecrit_fichiers_mapping
from documents.indexeur.indexeur import ReponseDocumentMaitriseEnSucces


def test_ecrit_le_fichier_de_mapping(tmp_path):
    chemin_html = tmp_path / "faq.html"
    chemin_html.touch()

    reponse = ReponseDocumentMaitriseEnSucces(
        id="doc123",
        name="faq.html",
        collection_id="12345",
        created_at="",
        updated_at="",
        mapping={"qui-est-le-directeur-de-lanssi": "Vincent Strubel."},
        chemin_source=str(chemin_html),
    )

    ecrit_fichiers_mapping([reponse])

    mapping_path = tmp_path / "faq.mapping.json"
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    assert mapping_path.exists()
    assert mapping["qui-est-le-directeur-de-lanssi"] == "Vincent Strubel."
