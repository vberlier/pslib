__all__ = ["PslibError", "ServerConnectionFailed", "InvalidPayloadFormat"]


class PslibError(Exception):
    pass


class ServerConnectionFailed(PslibError):
    pass


class InvalidPayloadFormat(PslibError):
    pass
