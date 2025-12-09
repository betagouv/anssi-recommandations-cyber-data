import time
from functools import wraps
from typing import Any, Callable
from deepeval.test_case import LLMTestCase
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    TypeEvenement,
    Donnees,
)


def mesurer_temps(
    adaptateur_journal: AdaptateurJournal = fabrique_adaptateur_journal(),
) -> Callable:
    def decorateur(fonction: Callable) -> Callable:
        @wraps(fonction)
        def fonction_mesuree(*args: Any, **kwargs: Any) -> Any:
            debut = time.perf_counter()
            resultat = fonction(*args, **kwargs)
            fin = time.perf_counter()
            duree = (fin - debut) * 1000  # en millisecondes
            liste_cas_de_test = args[1] if len(args) > 1 else []
            noms_cas_de_test = None
            if isinstance(liste_cas_de_test, list) and len(liste_cas_de_test) > 0:
                match liste_cas_de_test[0]:
                    case LLMTestCase():
                        noms_cas_de_test = ", ".join(
                            list(
                                map(
                                    lambda cas_de_test: f"{cas_de_test.name}",
                                    liste_cas_de_test,
                                )
                            )
                        )

            consigne = {
                "nom_fonction": fonction.__name__,
                "duree": duree,
            }
            if noms_cas_de_test is not None:
                consigne["cas_de_test"] = noms_cas_de_test
            adaptateur_journal.enregistre(
                TypeEvenement.TEMPS_EVALUATION_MESURE,
                Donnees.model_validate(consigne),
            )
            adaptateur_journal.ferme_connexion()

            return resultat

        return fonction_mesuree

    return decorateur
