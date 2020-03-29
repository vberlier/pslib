__all__ = [
    "PslibError",
    "ServerConnectionFailed",
    "InvalidPayloadFormat",
    "InvalidMessageParameters",
]


class PslibError(Exception):
    pass


class ServerConnectionFailed(PslibError):
    pass


class InvalidPayloadFormat(PslibError):
    pass


class InvalidMessageParameters(PslibError):
    pass
