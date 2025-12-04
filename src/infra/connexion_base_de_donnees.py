from functools import wraps
import psycopg2


def avec_connexion(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        connexion = None
        try:
            connexion = psycopg2.connect(
                host=self._configuration.hote,
                database=self._configuration.nom,
                user=self._configuration.utilisateur,
                password=self._configuration.mot_de_passe,
                port=self._configuration.port,
            )
            connexion.autocommit = True
            self._connexion = connexion
            return func(self, *args, **kwargs)
        finally:
            if connexion:
                connexion.close()

    return wrapper
