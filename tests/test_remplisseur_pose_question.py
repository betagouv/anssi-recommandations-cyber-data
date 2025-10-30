from pathlib import Path
import httpx
import respx
import pytest

from lecteur_csv import LecteurCSV
from configuration import recupere_configuration, MQC
from remplisseur_reponses import (
    RemplisseurReponses,
    EcrivainSortie,
    ClientMQCHTTP,
    HorlogeSysteme,
    construit_base_url,
    formate_route_pose_question,
)


def cree_reponse_mock(reponse: str, question: str) -> httpx.Response:
    return httpx.Response(
        200, json={"reponse": reponse, "paragraphes": [], "question": question}
    )


@pytest.fixture()
def configuration() -> MQC:
    return recupere_configuration().mqc


@respx.mock
def test_remplissage_appelle_api_pour_chaque_question(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    route = respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("X", "Q1?")
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    remplisseur.remplit_ligne(lecteur)
    remplisseur.remplit_ligne(lecteur)

    assert route.called
    assert route.call_count == 2


@respx.mock
def test_pose_question_retourne_reponse_question_structuree(configuration: MQC):
    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

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

    client = ClientMQCHTTP(cfg=configuration)
    resultat = client.pose_question("Ma question?")

    assert resultat.reponse == "Voici la réponse"
    assert resultat.question == "Ma question?"
    assert len(resultat.paragraphes) == 1
    assert resultat.paragraphes[0].score_similarite == 0.85
    assert resultat.paragraphes[0].nom_document == "Guide sécurité"


@respx.mock
def test_remplissage_insere_reponses_dans_colonne(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("mocked", "Q1?"))

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne1_enrichie = remplisseur.remplit_ligne(lecteur)
    ligne2_enrichie = remplisseur.remplit_ligne(lecteur)

    assert ligne1_enrichie["Réponse Bot"] == "mocked"
    assert ligne2_enrichie["Réponse Bot"] == "mocked"
    assert "Contexte" in ligne1_enrichie
    assert ligne1_enrichie["Contexte"] == ""
    assert ligne2_enrichie["Contexte"] == ""


@respx.mock
def test_remplissage_ajoute_colonne_context_avec_paragraphes(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

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

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    assert "Contexte" in ligne_enrichie
    assert "Contenu test" in str(ligne_enrichie["Contexte"])


@respx.mock
def test_remplissage_ajoute_colonne_context_avec_deux_paragraphes_separes_par_marqueur(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

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

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    assert (
        "Premier paragraphe${SEPARATEUR_DOCUMENT}Deuxième paragraphe"
        == ligne_enrichie["Contexte"]
    )


@respx.mock
def test_remplissage_ajoute_colonne_contenant_nom_document_qui_liste_origine_des_paragraphes(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

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

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    assert "Noms Documents" in ligne_enrichie
    assert ligne_enrichie["Noms Documents"] == [
        "Guide de sécurité",
        "Manuel utilisateur",
    ]


@respx.mock
def test_remplissage_ajoute_colonne_nom_document_liste_vide_si_aucun_paragraphe(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("Réponse", "Q1?"))

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    assert "Noms Documents" in ligne_enrichie
    assert ligne_enrichie["Noms Documents"] == []


@respx.mock
def test_remplissage_ajoute_colonne_numeros_page_de_tous_les_paragraphes(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

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

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    assert "Numéros Page" in ligne_enrichie
    assert ligne_enrichie["Numéros Page"] == [5, 12]


@respx.mock
def test_remplissage_ajoute_colonne_numeros_page_retourne_liste_vide_si_aucun_paragraphe(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nQ1?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("Réponse", "Q1?"))

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)
    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    assert "Numéros Page" in ligne_enrichie
    assert ligne_enrichie["Numéros Page"] == []


@respx.mock
def test_ecriture_cree_fichier_dans_bon_dossier(tmp_path: Path, configuration: MQC):
    (tmp_path / "donnees" / "sortie").mkdir(parents=True, exist_ok=True)
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)
    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("OK", "A?"))

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(
        ligne_enrichie, prefixe="evaluation"
    )

    assert chemin_csv.parent == tmp_path / "donnees" / "sortie"


@respx.mock
def test_ecriture_nom_fichier_contient_date(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)
    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("OK", "A?"))

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)
    ligne_enrichie = remplisseur.remplit_ligne(lecteur)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(
        ligne_enrichie, prefixe="evaluation"
    )

    assert "evaluation_" in chemin_csv.name


@respx.mock
def test_ecriture_contenu_csv_complet(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "eval.csv"
    fichier.write_text("Question type\nA?\nB?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)
    respx.post(f"{base}{chemin}").mock(return_value=cree_reponse_mock("OK", "A?"))

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )

    ligne1_enrichie = remplisseur.remplit_ligne(lecteur)
    chemin_csv = ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne1_enrichie, "evaluation")

    ligne2_enrichie = remplisseur.remplit_ligne(lecteur)
    ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne2_enrichie, "evaluation")

    contenu = chemin_csv.read_text(encoding="utf-8").splitlines()
    assert contenu[0].startswith("Question type")
    assert "A?,OK" in contenu[1]
    assert "B?,OK" in contenu[2]


def test_pose_question_declenche_exception_si_serveur_injoignable(configuration):
    client = ClientMQCHTTP(cfg=configuration)

    with respx.mock:
        respx.post(f"{client._base}{client._route}").mock(
            side_effect=httpx.ConnectError("connexion refusée")
        )
        with pytest.raises(RuntimeError) as exc:
            client.pose_question("Test ?")

    assert "Serveur MQC injoignable" in str(exc.value)


@pytest.mark.parametrize("valeur_donnee", ["foo", "bar", "fou42", "bar42"])
def test_methode_desinfecte_prefixe_retourne_a_l_identique_contenu_alphanumerique(
    valeur_donnee: str,
):
    valeur_desinfectee = EcrivainSortie._desinfecte_prefixe(valeur_donnee)
    assert valeur_desinfectee == valeur_donnee


@pytest.mark.parametrize(
    "valeur_infectee, valeur_desinfectee_attendue",
    [("foo/", "foo_"), ("bar*", "bar_"), ("bar.", "bar_"), ("bar./*", "bar___")],
)
def test_methode_desinfecte_prefixe_nettoie_le_contenu_non_alphanumerique(
    valeur_infectee, valeur_desinfectee_attendue
):
    valeur_desinfectee = EcrivainSortie._desinfecte_prefixe(valeur_infectee)
    assert valeur_desinfectee == valeur_desinfectee_attendue


@respx.mock
def test_remplit_ligne_enrichit_ligne_avec_reponse_bot(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type,Contexte\nQ1?,contexte\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("reponse_test", "Q1?")
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    ligne_enrichie = remplisseur.remplit_ligne(LecteurCSV(fichier))

    assert ligne_enrichie["Question type"] == "Q1?"
    assert ligne_enrichie["Réponse Bot"] == "reponse_test"


@respx.mock
def test_remplit_ligne_ecrit_bien_le_contexte(tmp_path: Path, configuration: MQC):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type,Contexte\nQ1?,contexte\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

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

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    ligne_enrichie = remplisseur.remplit_ligne(LecteurCSV(fichier))

    assert (
        ligne_enrichie["Contexte"]
        == "Premier paragraphe${SEPARATEUR_DOCUMENT}Deuxième paragraphe"
    )
    assert ligne_enrichie["Réponse Bot"] == "reponse_test"


@respx.mock
def test_remplit_ligne_avec_lecteur_traite_lignes_sequentiellement(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("reponse_test", "Q1?")
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)

    ligne1_enrichie = remplisseur.remplit_ligne(lecteur)
    ligne2_enrichie = remplisseur.remplit_ligne(lecteur)

    assert ligne1_enrichie["Question type"] == "Q1?"
    assert ligne1_enrichie["Réponse Bot"] == "reponse_test"

    assert ligne2_enrichie["Question type"] == "Q2?"
    assert ligne2_enrichie["Réponse Bot"] == "reponse_test"


@respx.mock
def test_ecrit_ligne_depuis_lecteur_csv_ecrit_ligne_par_ligne(
    tmp_path: Path, configuration: MQC
):
    fichier = tmp_path / "test.csv"
    fichier.write_text("Question type\nQ1?\nQ2?\n", encoding="utf-8")

    base = construit_base_url(configuration)
    chemin = formate_route_pose_question(configuration)

    respx.post(f"{base}{chemin}").mock(
        return_value=cree_reponse_mock("reponse_test", "Q1?")
    )

    client = ClientMQCHTTP(cfg=configuration)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("sortie"), horloge=horloge
    )

    ligne1_enrichie = remplisseur.remplit_ligne(lecteur)

    chemin_sortie = ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne1_enrichie, "test")

    contenu = chemin_sortie.read_text(encoding="utf-8").strip().split("\n")
    assert len(contenu) == 2
    assert "Question type,Réponse Bot" in contenu[0]
    assert "Q1?,reponse_test" in contenu[1]

    ligne2_enrichie = remplisseur.remplit_ligne(lecteur)

    ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne2_enrichie, "test")

    contenu = chemin_sortie.read_text(encoding="utf-8").strip().split("\n")
    assert len(contenu) == 3
    assert "Q2?,reponse_test" in contenu[2]
