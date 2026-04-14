import multiprocessing as mp


class Multiprocesseur:
    def __init__(self, nombre_processus: int = 7):
        self._nombre_processus = nombre_processus

    def execute(self, func, iterable) -> list:
        pool = mp.Pool(processes=self._nombre_processus)
        try:
            return pool.map(func, iterable)
        finally:
            pool.close()
            pool.join()
