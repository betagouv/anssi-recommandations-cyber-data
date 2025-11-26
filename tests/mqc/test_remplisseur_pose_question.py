from pathlib import Path
import httpx
import asyncio
import respx
import pytest

from configuration import MQC
from infra.lecteur_csv import LecteurCSV
from mqc.remplisseur_reponses import (
    RemplisseurReponses,
    ClientMQCHTTPAsync,
    construit_base_url,
    formate_route_pose_question,
)


def cree_reponse_mock(reponse: str, question: str) -> httpx.Response:
    return httpx.Response(
        200, json={"reponse": reponse, "paragraphes": [], "question": question}
    )


@respx.mock
def test_remplissage_appelle_api_pour_chaque_question(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    route = respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("X", "Q1?")
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert route.called
    assert route.call_count == 2


@respx.mock
def test_pose_question_retourne_reponse_question_structuree(configuration_mqc: MQC):
    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    reponse_json = {
        "reponse": "Voici la réponse",
        "paragraphes": [
            {
                "score_similarite": 0.85,
                "numero_page": 1,
                "url": "https://example.com/doc1",
                "nom_document": "Guide sécurité",
                "contenu": "Contenu du paragraphe",
            }
        ],
        "question": "Ma question?",
    }

    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_json)
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    resultat = asyncio.run(client.pose_question("Ma question?"))

    assert resultat.reponse == "Voici la réponse"
    assert resultat.question == "Ma question?"
    assert len(resultat.paragraphes) == 1
    assert resultat.paragraphes[0].score_similarite == 0.85
    assert resultat.paragraphes[0].nom_document == "Guide sécurité"


@respx.mock
def test_remplissage_insere_reponses_dans_colonne(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("mocked", "Q1?"))

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne1_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]
    ligne2_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert ligne1_enrichie["Réponse Bot"] == "mocked"
    assert ligne2_enrichie["Réponse Bot"] == "mocked"
    assert "Contexte" in ligne1_enrichie
    assert ligne1_enrichie["Contexte"] == ""
    assert ligne2_enrichie["Contexte"] == ""


@respx.mock
def test_remplissage_ajoute_colonne_context_avec_paragraphes(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    reponse_avec_paragraphes = {
        "reponse": "Réponse test",
        "paragraphes": [
            {
                "score_similarite": 0.9,
                "numero_page": 5,
                "url": "https://test.com",
                "nom_document": "Doc test",
                "contenu": "Contenu test",
            }
        ],
        "question": "Q1?",
    }

    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes)
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert "Contexte" in ligne_enrichie
    assert "Contenu test" in str(ligne_enrichie["Contexte"])


@respx.mock
def test_remplissage_ajoute_colonne_context_avec_deux_paragraphes_separes_par_marqueur(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    reponse_avec_paragraphes_multiples = {
        "reponse": "Réponse test",
        "paragraphes": [
            {
                "score_similarite": 0.9,
                "numero_page": 5,
                "url": "https://test.com",
                "nom_document": "Doc test",
                "contenu": "Premier paragraphe",
            },
            {
                "score_similarite": 0.8,
                "numero_page": 6,
                "url": "https://test2.com",
                "nom_document": "Doc test 2",
                "contenu": "Deuxième paragraphe",
            },
        ],
        "question": "Q1?",
    }

    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes_multiples)
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert (
        "Premier paragraphe${SEPARATEUR_DOCUMENT}Deuxième paragraphe"
        == ligne_enrichie["Contexte"]
    )


@respx.mock
def test_remplissage_ajoute_colonne_contenant_nom_document_qui_liste_origine_des_paragraphes(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    reponse_avec_paragraphes_multiples = {
        "reponse": "Réponse test",
        "paragraphes": [
            {
                "score_similarite": 0.9,
                "numero_page": 5,
                "url": "https://test.com",
                "nom_document": "Guide de sécurité",
                "contenu": "Premier paragraphe",
            },
            {
                "score_similarite": 0.8,
                "numero_page": 6,
                "url": "https://test2.com",
                "nom_document": "Manuel utilisateur",
                "contenu": "Deuxième paragraphe",
            },
        ],
        "question": "Q1?",
    }

    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes_multiples)
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert "Noms Documents" in ligne_enrichie
    assert ligne_enrichie["Noms Documents"] == [
        "Guide de sécurité",
        "Manuel utilisateur",
    ]


@respx.mock
def test_remplissage_ajoute_colonne_nom_document_liste_vide_si_aucun_paragraphe(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("Réponse", "Q1?"))

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert "Noms Documents" in ligne_enrichie
    assert ligne_enrichie["Noms Documents"] == []


@respx.mock
def test_remplissage_ajoute_colonne_numeros_page_de_tous_les_paragraphes(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    reponse_avec_paragraphes_multiples = {
        "reponse": "Réponse test",
        "paragraphes": [
            {
                "score_similarite": 0.9,
                "numero_page": 5,
                "url": "https://test.com",
                "nom_document": "Guide de sécurité",
                "contenu": "Premier paragraphe",
            },
            {
                "score_similarite": 0.8,
                "numero_page": 12,
                "url": "https://test2.com",
                "nom_document": "Manuel utilisateur",
                "contenu": "Deuxième paragraphe",
            },
        ],
        "question": "Q1?",
    }

    respx.post(f"{base}{chemin}").mock(
        return_value=httpx.Response(200, json=reponse_avec_paragraphes_multiples)
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert "Numéros Page" in ligne_enrichie
    assert ligne_enrichie["Numéros Page"] == [5, 12]


@respx.mock
def test_remplissage_ajoute_colonne_numeros_page_retourne_liste_vide_si_aucun_paragraphe(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("Réponse", "Q1?"))

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = asyncio.run(remplisseur.remplit_lot_lignes(lecteur, 1))[0]

    assert "Numéros Page" in ligne_enrichie
    assert ligne_enrichie["Numéros Page"] == []


def test_pose_question_declenche_exception_si_serveur_injoignable(configuration_mqc):
    client = ClientMQCHTTPAsync(cfg=configuration_mqc)

    with respx.mock:
        respx.post(f"{client._base}{client._route}").mock(
            side_effect=httpx.ConnectError("connexion refusée")
        )
        with pytest.raises(RuntimeError) as exc:
            asyncio.run(client.pose_question("Test ?"))

    assert "Serveur MQC injoignable" in str(exc.value)


@respx.mock
def test_remplit_ligne_enrichit_ligne_avec_reponse_bot(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type,Contexte\nQ1?,contexte\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("reponse_test", "Q1?")
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    ligne_enrichie = asyncio.run(
        remplisseur.remplit_lot_lignes(LecteurCSV(fichier), 1)
    )[0]

    assert ligne_enrichie["Question type"] == "Q1?"
    assert ligne_enrichie["Réponse Bot"] == "reponse_test"


@respx.mock
def test_remplit_ligne_ecrit_bien_le_contexte(tmp_path: Path, configuration_mqc: MQC):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type,Contexte\nQ1?,contexte\n", encoding="utf-8")

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    reponse_mock_avec_paragraphe = httpx.Response(
        200,
        json={
            "reponse": "reponse_test",
            "paragraphes": [
                {
                    "score_similarite": 0.9,
                    "numero_page": 5,
                    "url": "https://test.com",
                    "nom_document": "Doc test",
                    "contenu": "Premier paragraphe",
                },
                {
                    "score_similarite": 0.8,
                    "numero_page": 6,
                    "url": "https://test2.com",
                    "nom_document": "Doc test 2",
                    "contenu": "Deuxième paragraphe",
                },
            ],
            "question": "Q1?",
        },
    )
    respx.post(f"{base}{chemin}").mock(return_value=reponse_mock_avec_paragraphe)

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    ligne_enrichie = asyncio.run(
        remplisseur.remplit_lot_lignes(LecteurCSV(fichier), 1)
    )[0]

    assert (
        ligne_enrichie["Contexte"]
        == "Premier paragraphe${SEPARATEUR_DOCUMENT}Deuxième paragraphe"
    )
    assert ligne_enrichie["Réponse Bot"] == "reponse_test"


@respx.mock
@pytest.mark.asyncio
async def test_remplit_ligne_avec_lecteur_traite_lignes_sequentiellement(
    tmp_path: Path, configuration_mqc: MQC
):
    fichier = tmp_path / "test.csv"
    fichier.write_text(
        "Question type\nQ1?\nQ2?\nQ3?\nQ4?\nQ5?\nQ6?\nQ7?", encoding="utf-8"
    )

    base = construit_base_url(configuration_mqc)
    chemin = formate_route_pose_question(configuration_mqc)

    respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("reponse_test", "Q1?")
    )

    client = ClientMQCHTTPAsync(cfg=configuration_mqc)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)

    ligne1_enrichie = await remplisseur.remplit_lot_lignes(lecteur, 5)
    ligne2_enrichie = await remplisseur.remplit_lot_lignes(lecteur, 2)

    assert [ligne["Question type"] for ligne in ligne1_enrichie] == [
        "Q1?",
        "Q2?",
        "Q3?",
        "Q4?",
        "Q5?",
    ]
    assert [ligne["Question type"] for ligne in ligne2_enrichie] == [
        "Q6?",
        "Q7?",
    ]
    assert [ligne["Réponse Bot"] for ligne in ligne1_enrichie] == [
        "reponse_test",
        "reponse_test",
        "reponse_test",
        "reponse_test",
        "reponse_test",
    ]
    assert [ligne["Réponse Bot"] for ligne in ligne2_enrichie] == [
        "reponse_test",
        "reponse_test",
    ]
