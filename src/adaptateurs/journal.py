from configuration import recupere_configuration, BaseDeDonnees
import psycopg2.extras
from abc import ABC, abstractmethod
from enum import StrEnum
from pydantic import BaseModel, ConfigDict
import psycopg2
from psycopg2.extensions import connection
import datetime

from infra.connexion_base_de_donnees import avec_connexion


class Donnees(BaseModel):
    model_config = ConfigDict(extra="allow")


class TypeEvenement(StrEnum):
    TEMPS_EVALUATION_MESURE = "TEMPS_EVALUATION_MESURE"
    EVALUATION_CALCULEE = "EVALUATION_CALCULEE"


class AdaptateurJournal(ABC):
    @abstractmethod
    def enregistre(self, type: TypeEvenement, donnees: Donnees) -> None:
        pass

    @abstractmethod
    def ferme_connexion(self) -> None:
        pass


class AdaptateurJournalMemoire(AdaptateurJournal):
    def __init__(self):
        self._evenements = []
        self.ferme_connexion_a_ete_appelee = 0

    def enregistre(self, type: TypeEvenement, donnees: Donnees) -> None:
        self._evenements.append({"type": type, "donnees": donnees.model_dump()})

    def les_evenements(self):
        return self._evenements

    def ferme_connexion(self) -> None:
        self.ferme_connexion_a_ete_appelee += 1
        return None


class AdaptateurJournalPostgres(AdaptateurJournal):
    _connexion: connection | None = None

    def __init__(self, configuration: BaseDeDonnees):
        self._configuration = configuration

    @avec_connexion
    def enregistre(self, type: TypeEvenement, donnees: Donnees):
        curseur = self._le_curseur()
        curseur.execute(
            "INSERT INTO journal_mqc.evenements (date, type, donnees) VALUES (%s, %s, %s)",
            (datetime.datetime.now(), type, donnees.model_dump_json()),
        )

    def _le_curseur(self):
        return self._connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def ferme_connexion(self) -> None:
        pass


def fabrique_adaptateur_journal() -> AdaptateurJournal:
    configuration = recupere_configuration()
    return (
        AdaptateurJournalPostgres(configuration.base_de_donnees_journal)
        if configuration.base_de_donnees_journal is not None
        else AdaptateurJournalMemoire()
    )
