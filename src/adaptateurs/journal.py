from configuration import recupere_configuration, BaseDeDonnees
import psycopg2.extras
from abc import ABC, abstractmethod
from enum import StrEnum
from pydantic import BaseModel, ConfigDict
import psycopg2
import datetime


class Donnees(BaseModel):
    model_config = ConfigDict(extra="allow")


class TypeEvenement(StrEnum):
    EVALUATION_CALCULEE = "EVALUATION_CALCULEE"


class AdaptateurJournal(ABC):
    @abstractmethod
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        pass


class AdaptateurJournalMemoire(AdaptateurJournal):
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        self._evenements.append({"type": type, "donnees": donnees.model_dump()})

    def __init__(self):
        self._evenements = []

    def enregistrer(self, evenement):
        self._evenements.append(evenement)

    def les_evenements(self):
        return self._evenements


class AdaptateurJournalPostgres(AdaptateurJournal):
    def __init__(self, configuration: BaseDeDonnees):
        self._connexion = psycopg2.connect(
            host=configuration.hote,
            database=configuration.nom,
            user=configuration.utilisateur,
            password=configuration.mot_de_passe,
            port=configuration.port,
        )
        self._connexion.autocommit = True

    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees):
        curseur = self._get_curseur()
        curseur.execute(
            "INSERT INTO journal_mqc.evenements (date, type, donnees) VALUES (%s, %s, %s)",
            (datetime.datetime.now(), type, donnees.model_dump_json()),
        )

    def _get_curseur(self):
        return self._connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def ferme_connexion(self) -> None:
        if self._connexion:
            self._connexion.close()


def fabrique_adaptateur_journal() -> AdaptateurJournal:
    configuration = recupere_configuration()
    return (
        AdaptateurJournalPostgres(configuration.base_de_donnees_journal)
        if configuration.base_de_donnees_journal
        else AdaptateurJournalMemoire()
    )
