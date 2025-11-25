from pathlib import Path
from unittest.mock import Mock

from evalap.lance_experience import lance_experience
from infra.memoire.evalap import EvalapClientDeTest


def test_lance_experience(
    configuration,
    cree_fichier_csv_avec_du_contenu,
    tmp_path: Path,
    reponse_a_l_ajout_d_un_dataset,
    reponse_a_la_creation_d_une_experience,
    reponse_a_la_lecture_d_une_experience,
):
    session = Mock()
    client = EvalapClientDeTest(configuration, session=session)
    client.reponse_ajoute_dataset(reponse_a_l_ajout_d_un_dataset)
    client.reponse_cree_experience(reponse_a_la_creation_d_une_experience)
    client.reponse_lit_experience(reponse_a_la_lecture_d_une_experience)
    fichier_csv = cree_fichier_csv_avec_du_contenu(
        "REF Guide,REF Question,Que stion type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\nGAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]",
        tmp_path,
    )

    experience_id_cree = lance_experience(
        client, configuration, 1, "nom_experience", fichier_csv
    )

    assert experience_id_cree == 1
