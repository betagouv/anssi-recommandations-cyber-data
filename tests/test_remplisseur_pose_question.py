from pathlib import Path
import httpx
import respx
import pytest

from src.configuration import recupere_configuration, MQC
from src.remplisseur_reponses import (
    RemplisseurReponses,
    EcrivainSortie,
    ClientMQCHTTP,
    HorlogeSysteme,
    construit_base_url,
    formate_route_pose_question,
)
from unittest.mock import patch, Mock


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

    list(remplisseur.remplit_fichier_flux(fichier))

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

    lignes = list(remplisseur.remplit_fichier_flux(fichier))

    assert list(map(lambda x: x["Réponse Bot"], lignes)) == ["mocked", "mocked"]
    assert list(map(lambda x: x["Contexte"], lignes)) == ["", ""]


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
    lignes = list(remplisseur.remplit_fichier_flux(fichier))

    assert "Contexte" in lignes[0].keys()
    context_str = str(lignes[0]["Contexte"])
    assert "Contenu test" in context_str


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
    lignes = list(remplisseur.remplit_fichier_flux(fichier))

    assert len(lignes) == 1
    context_str = str(lignes[0]["Contexte"])
    assert "Premier paragraphe${SEPARATEUR_DOCUMENT}Deuxième paragraphe" == context_str


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
    generateur = remplisseur.remplit_fichier_flux(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_fichier_depuis_generateur(
        generateur, prefixe="evaluation"
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
    generateur = remplisseur.remplit_fichier_flux(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_fichier_depuis_generateur(
        generateur, prefixe="evaluation"
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
    generateur = remplisseur.remplit_fichier_flux(fichier)

    horloge = HorlogeSysteme()
    ecrivain = EcrivainSortie(
        racine=tmp_path, sous_dossier=Path("donnees/sortie"), horloge=horloge
    )
    chemin_csv = ecrivain.ecrit_fichier_depuis_generateur(
        generateur, prefixe="evaluation"
    )

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


def test_remplit_fichier_flux_genere_lignes_une_par_une():
    client_mock = Mock()
    client_mock.pose_question.return_value.reponse = "test"
    client_mock.pose_question.return_value.paragraphes = []

    lecteur_mock = Mock()
    lecteur_mock.iterer_lignes.return_value = iter(
        [{"Question type": "Q1?"}, {"Question type": "Q2?"}]
    )

    remplisseur = RemplisseurReponses(client_mock)

    with patch("src.remplisseur_reponses.LecteurCSV", return_value=lecteur_mock):
        generateur = remplisseur.remplit_fichier_flux(Path("/fake"))
        premiere_ligne = next(generateur)
        assert client_mock.pose_question.call_count == 1
        assert premiere_ligne["Question type"] == "Q1?"
        deuxieme_ligne = next(generateur)
        assert client_mock.pose_question.call_count == 2
        assert deuxieme_ligne["Question type"] == "Q2?"


def test_ecrit_fichier_flux_ecrit_au_fur_et_mesure():
    def generateur_simule():
        yield {"Question type": "Q1?", "Réponse Bot": "R1"}
        yield {"Question type": "Q2?", "Réponse Bot": "R2"}

    horloge_mock = Mock()
    horloge_mock.aujourd_hui.return_value = "2025-01-01_12-00-00"

    ecrivain_mock = Mock(spec=EcrivainSortie)
    ecrivain_mock.ecrit_fichier_depuis_generateur.return_value = Path("/faux/test.csv")

    generateur = generateur_simule()
    ecrivain_mock.ecrit_fichier_depuis_generateur(generateur, prefixe="test")

    ecrivain_mock.ecrit_fichier_depuis_generateur.assert_called_once()
