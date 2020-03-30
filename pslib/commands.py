__all__ = ["GlobalCommandsMixin"]


from .messages import UpdateUserMessage, PrivateMessage, QueryResponseMessage
from .errors import ServerLoginFailed, PrivateMessageError
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
            async for message in self.client.listen(UpdateUserMessage):
                if message.userid == userid:
                    break

    async def private_message(self, receiver, content):
        receiver = into_id(receiver)

        async with self.client.send_command("pm", receiver, content):
            async for message in self.client.listen(PrivateMessage):
                if into_id(message.receiver) == receiver:
                    if message.content.startswith("/error"):
                        raise PrivateMessageError(message.content[7:])
                    break

    async def query_battles(self, format="", minimum_elo=None, username_prefix=""):
        async with self.client.send_command(
            "cmd roomlist",
            format,
            "none" if minimum_elo is None else minimum_elo,
            username_prefix,
        ):
            async for response in self.client.listen(QueryResponseMessage):
                if response.querytype == "roomlist":
                    return [
                        self.client.rooms[battle_id]
                        for battle_id in response.result["rooms"]
                    ]
