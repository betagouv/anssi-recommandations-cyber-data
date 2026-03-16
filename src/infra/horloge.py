import datetime as dt


class HorlogeSysteme:
    def aujourd_hui(self) -> str:
        return str(dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
