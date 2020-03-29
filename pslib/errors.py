__all__ = ["PslibError", "ShowdownConnectionFailed", "InvalidPayloadFormat"]


class PslibError(Exception):
    pass


class ShowdownConnectionFailed(PslibError):
    def __init__(self):
        super().__init__("Didn't receive server acknowledgment")


class InvalidPayloadFormat(PslibError):
    pass
