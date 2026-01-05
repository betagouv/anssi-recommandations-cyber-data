import multiprocessing as mp


class Multiprocesseur:
    def execute(self, func, iterable) -> list:
        with mp.Pool(processes=10) as pool:
            return pool.map(func, iterable)
