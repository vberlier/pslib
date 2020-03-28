__all__ = ["PslibError", "ShowdownConnectionFailed"]


class PslibError(Exception):
    pass


class ShowdownConnectionFailed(PslibError):
    def __init__(self):
        super().__init__("Didn't receive server acknowledgment")
