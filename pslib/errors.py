__all__ = [
    "PslibError",
    "ServerConnectionFailed",
    "InvalidPayloadFormat",
    "InvalidMessageParameters",
    "ServerIdNotSpecified",
    "InvalidServerActionResponse",
    "ServerLoginFailed",
    "PrivateMessageError",
    "InvalidRoomId",
    "JoiningRoomFailed",
    "ServerResponseTimeout",
    "ReceivedErrorMessage",
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


class ServerLoginFailed(PslibError):
    pass


class PrivateMessageError(PslibError):
    pass


class InvalidRoomId(PslibError):
    pass


class JoiningRoomFailed(PslibError):
    pass


class ServerResponseTimeout(PslibError):
    pass


class ReceivedErrorMessage(PslibError):
    pass
