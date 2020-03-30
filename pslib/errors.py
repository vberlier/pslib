__all__ = [
    "PslibError",
    "ServerConnectionFailed",
    "InvalidPayloadFormat",
    "InvalidMessageParameters",
    "ServerIdNotSpecified",
    "InvalidServerActionResponse",
]


class PslibError(Exception):
    pass


class ServerConnectionFailed(PslibError):
    pass


class InvalidPayloadFormat(PslibError):
    pass


class InvalidMessageParameters(PslibError):
    pass


class ServerIdNotSpecified(PslibError):
    pass


class InvalidServerActionResponse(PslibError):
    pass
