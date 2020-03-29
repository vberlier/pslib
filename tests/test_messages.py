import pytest

from pslib import (
    parse_message,
    UnrecognizedMessage,
    PlainTextMessage,
    UpdateUserMessage,
    InvalidMessageParameters,
)


@pytest.mark.parametrize(
    "raw_message",
    [
        "|something|foo",
        "Hello, world!",
        '|updateuser| Guest 3642588|0|102|{"isSysop":false,"isStaff":false,"blockChallenges":false,"blockPMs":false,"ignoreTickets":false,"lastConnected":1585447346979,"lastDisconnected":0,"inviteOnlyNextBattle":false,"statusType":"online"}',
    ],
)
def test_serialize(raw_message):
    assert parse_message(raw_message).serialize() == raw_message


def test_unrecognized():
    assert parse_message("|something|foo") == UnrecognizedMessage("something", "foo")


def test_plain_text():
    assert parse_message("Hello, world!") == PlainTextMessage("", "Hello, world!")


def test_update_user():
    message = parse_message(
        '|updateuser| Guest 3642588|0|102|{"isSysop":false,"isStaff":false,"blockChallenges":false,"blockPMs":false,"ignoreTickets":false,"lastConnected":1585447346979,"lastDisconnected":0,"inviteOnlyNextBattle":false,"statusType":"online"}'
    )

    assert isinstance(message, UpdateUserMessage)
    assert message.user == " Guest 3642588"
    assert message.named == False
    assert message.avatar == 102
    assert message.settings == {
        "isSysop": False,
        "isStaff": False,
        "blockChallenges": False,
        "blockPMs": False,
        "ignoreTickets": False,
        "lastConnected": 1585447346979,
        "lastDisconnected": 0,
        "inviteOnlyNextBattle": False,
        "statusType": "online",
    }


def test_update_user_wrong_params():
    with pytest.raises(InvalidMessageParameters):
        parse_message("|updateuser| Guest 3642588|0|102")
