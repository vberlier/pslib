__all__ = ["GlobalCommandsMixin"]


from .messages import QueryResponseMessage


class GlobalCommandsMixin:
    async def query_battles(self):
        async with self.client.send_command("query", "roomlist"):
            async for response in self.listen(QueryResponseMessage):
                if response.querytype == "roomlist":
                    return [
                        self.rooms[battle_id] for battle_id in response.result["rooms"]
                    ]
