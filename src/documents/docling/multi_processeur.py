import multiprocessing as mp


class Multiprocesseur:
    def execute(self, func, iterable) -> list:
        pool = mp.Pool(processes=5)
        try:
            return pool.map(func, iterable)
        finally:
            pool.close()
            pool.join()
