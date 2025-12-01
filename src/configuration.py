import os
from typing_extensions import NamedTuple


class MQC(NamedTuple):
    port: int
    hote: str
    api_prefixe_route: str
    route_pose_question: str
    delai_attente_maximum: float


class Evalap(NamedTuple):
    url: str
    token_authentification: str


class Albert(NamedTuple):
    url: str
    cle_api: str


class BaseDeDonnees(NamedTuple):
    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    nom: str


class ParametresEvaluation(NamedTuple):
    taille_de_lot_collecte_mqc: int
    nb_processus_en_parallele_pour_deepeval: int


class Configuration(NamedTuple):
    mqc: MQC
    evalap: Evalap
    albert: Albert
    base_de_donnees_journal: BaseDeDonnees | None
    frequence_lecture: float
    est_evaluation_deepeval: bool
    parametres_deepeval: ParametresEvaluation


def recupere_configuration_postgres() -> BaseDeDonnees | None:
    db_host = os.getenv("DB_HOST")
    if db_host is None:
        return None
    return BaseDeDonnees(
        hote=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        utilisateur=os.getenv("DB_USER", "postgres"),
        mot_de_passe=os.getenv("DB_PASSWORD", "postgres"),
        nom=os.getenv("DB_NAME", "postgres"),
    )


def recupere_configuration() -> Configuration:
    configuration_mqc = MQC(
        port=int(os.getenv("MQC_PORT", "8002")),
        hote=os.getenv("MQC_HOTE", "localhost"),
        api_prefixe_route=os.getenv("MQC_API_PREFIXE_ROUTE", ""),
        route_pose_question=os.getenv("MQC_ROUTE_POSE_QUESTION", "pose_question"),
        delai_attente_maximum=float(os.getenv("MQC_DELAI_ATTENTE_MAXIMUM", 0.5)),
    )

    est_evaluation_deepeval = bool(os.getenv("EVALUATION_DEEPEVAL"))
    evalap: Evalap = Evalap(
        url=os.getenv("EVALAP_URL", "http://localhost:8000/v1"),
        token_authentification=os.getenv("EVALAP_TOKEN", ""),
    )

    albert: Albert = Albert(
        url=os.getenv("ALBERT_URL", "https://albert.api.etalab.gouv.fr/v1"),
        cle_api=os.getenv("ALBERT_CLE_API", "cle_api"),
    )

    base_de_donnees_journal: BaseDeDonnees | None = recupere_configuration_postgres()
    frequence_lecture = float(os.getenv("FREQUENCE_LECTURE", 10.0))

    parametres_deepeval = ParametresEvaluation(
        taille_de_lot_collecte_mqc=int(os.getenv("TAILLE_DE_LOT_COLLECTE_MQC", "10")),
        nb_processus_en_parallele_pour_deepeval=int(
            os.getenv("NB_PROCESSUS_EN_PARALLELE_POUR_DEEPEVAL", "4")
        ),
    )

    return Configuration(
        mqc=configuration_mqc,
        evalap=evalap,
        albert=albert,
        base_de_donnees_journal=base_de_donnees_journal,
        frequence_lecture=frequence_lecture,
        est_evaluation_deepeval=est_evaluation_deepeval,
        parametres_deepeval=parametres_deepeval,
    )
