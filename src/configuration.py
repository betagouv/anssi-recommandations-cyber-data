import os
from enum import StrEnum

from typing_extensions import NamedTuple, Optional

from documents.docling.chunker_docling import ChunkerDocling
from documents.docling.chunker_docling_mqc import ChunkerDoclingMQC
from jeopardy.client_albert_jeopardy import ConfigurationJeopardy


class MQC(NamedTuple):
    port: int
    hote: str
    api_prefixe_route: str
    route_pose_question: str
    delai_attente_maximum: float


class MQCData(NamedTuple):
    max_requetes_par_minute: int
    hote: str
    port: int


class IndexeurDocument(StrEnum):
    INDEXEUR_ALBERT = ("INDEXEUR_ALBERT",)
    INDEXEUR_DOCLING = ("INDEXEUR_DOCLING",)


class Albert(NamedTuple):
    url: str
    cle_api: str
    indexeur: IndexeurDocument
    modele: str
    chunker: Optional[ChunkerDocling] = None


class BaseDeDonnees(NamedTuple):
    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    nom: str


class ParametresEvaluation(NamedTuple):
    taille_de_lot_collecte_mqc: int
    nb_processus_en_parallele_pour_deepeval: int


class MSC(NamedTuple):
    url: str
    chemin_guides: str


class Configuration(NamedTuple):
    mqc: MQC
    albert: Albert
    base_de_donnees_journal: BaseDeDonnees | None
    parametres_deepeval: ParametresEvaluation
    msc: MSC
    mqc_data: MQCData
    jeopardy: ConfigurationJeopardy


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

    configuration_mqc_data = MQCData(
        port=int(os.getenv("MQC_DATA_PORT", "3000")),
        hote=os.getenv("MQC_DATA_HOTE", "localhost"),
        max_requetes_par_minute=int(
            os.getenv("MQC_DATA_MAX_REQUETES_PAR_MINUTE", "100")
        ),
    )

    indexeur_document = IndexeurDocument(os.getenv("INDEXEUR", "INDEXEUR_ALBERT"))
    chunker: ChunkerDocling | None = None
    if indexeur_document == IndexeurDocument.INDEXEUR_DOCLING:
        chunker = ChunkerDoclingMQC()

    albert: Albert = Albert(
        url=os.getenv("ALBERT_URL", "https://albert.api.etalab.gouv.fr/v1"),
        cle_api=os.getenv("ALBERT_CLE_API", "cle_api"),
        indexeur=indexeur_document,
        modele=os.getenv("ALBERT_MODELE", "openweight-medium"),
        chunker=chunker,
    )

    base_de_donnees_journal: BaseDeDonnees | None = recupere_configuration_postgres()

    parametres_deepeval = ParametresEvaluation(
        taille_de_lot_collecte_mqc=int(os.getenv("TAILLE_DE_LOT_COLLECTE_MQC", "10")),
        nb_processus_en_parallele_pour_deepeval=int(
            os.getenv("NB_PROCESSUS_EN_PARALLELE_POUR_DEEPEVAL", "4")
        ),
    )

    configuration_msc = MSC(
        url=os.getenv("MSC_URL_BASE", "https://messervices.cyber.gouv.fr"),
        chemin_guides=os.getenv("MSC_CHEMIN_GUIDES", "documents-guides"),
    )

    configuration_jeopardy = ConfigurationJeopardy(
        base_url=albert.url,
        cle_api=albert.cle_api,
        modele_generation=os.getenv("ALBERT_MODELE_JEOPARDY", "mistral-medium-2508"),
    )

    return Configuration(
        mqc=configuration_mqc,
        albert=albert,
        base_de_donnees_journal=base_de_donnees_journal,
        parametres_deepeval=parametres_deepeval,
        msc=configuration_msc,
        mqc_data=configuration_mqc_data,
        jeopardy=configuration_jeopardy,
    )
