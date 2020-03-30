__all__ = ["GlobalCommandsMixin"]


from .messages import QueryResponseMessage


class GlobalCommandsMixin:
    async def query_battles(self, format="", minimum_elo=None, username_prefix=""):
        async with self.client.send_command(
            "cmd roomlist",
            format,
            "none" if minimum_elo is None else minimum_elo,
            username_prefix,
        ):
            async for response in self.listen(QueryResponseMessage):
                if response.querytype == "roomlist":
                    return [
                        self.rooms[battle_id] for battle_id in response.result["rooms"]
                    ]
