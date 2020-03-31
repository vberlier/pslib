__all__ = ["GlobalCommandsMixin"]


from .messages import (
    UpdateUserMessage,
    PrivateMessage,
    QueryResponseMessage,
    DeinitMessage,
)
from .errors import (
    ServerLoginFailed,
    PrivateMessageError,
    InvalidRoomId,
    JoiningRoomFailed,
)
from .utils import into_id


class GlobalCommandsMixin:
    async def login(self, username, password=None, *, server_id=None):
        userid = into_id(username)

        data = (
            {
                "act": "getassertion",
                "userid": userid,
                "challstr": await self.client.state.challstr,
            }
            if password is None
            else {
                "act": "login",
                "name": username,
                "pass": password,
                "challstr": await self.client.state.challstr,
            }
        )

        response = await self.client.http.post_action(data, server_id=server_id)

        if password is None:
            if response.startswith(";"):
                raise ServerLoginFailed("Unavailable username")
            assertion = response
        else:
            if not response["actionsuccess"]:
                raise ServerLoginFailed("Invalid credentials")
            assertion = response["assertion"]

        async with self.client.send_command("trn", username, 0, assertion):
            await self.client.expect(UpdateUserMessage, userid=userid)

    async def private_message(self, receiver, content):
        receiver = into_id(receiver)

        async with self.client.send_command("pm", receiver, content):
            message = await self.client.expect(PrivateMessage, receiver=receiver)

            if message.content.startswith("/error"):
                raise PrivateMessageError(message.content[7:])

    async def query_battles(self, format="", minimum_elo=None, username_prefix=""):
        async with self.client.send_command(
            "cmd roomlist",
            format,
            "none" if minimum_elo is None else minimum_elo,
            username_prefix,
        ):
            response = await self.client.expect(
                QueryResponseMessage, querytype="roomlist"
            )
            return [
                self.client.rooms[battle_id] for battle_id in response.result["rooms"]
            ]

    async def join(self, room_id=None):
        if room_id is None:
            room_id = self.id

        if not room_id:
            raise InvalidRoomId("Expected valid room id")

        room = self.client.rooms[room_id]

        async with self.client.send_command("join", room_id):
            if not await room.state.joined:
                room.handle_leave()
                raise JoiningRoomFailed(f"Couldn't join room {room_id}")
            return room

    async def leave(self, room_id=None):
        if room_id is None:
            room_id = self.id

        if not room_id:
            raise InvalidRoomId("Expected valid room id")

        room = self.client.rooms[room_id]

        async with self.client.send_command("leave", room_id):
            await room.expect(DeinitMessage)
            room.handle_leave()
