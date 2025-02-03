from typing import Dict
from fastapi import WebSocket


class ChatSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int, user_id: int):
        await websocket.accept()
        self.active_connections[chat_id] = {user_id: websocket}

    def disconnect(self, chat_id: int, user_id: int):
        self.active_connections[chat_id].pop(user_id, None)

    async def send_data(self, data: Dict[str, any]):
        match data["data_type"]:
            case "text":
                await self._send_text(data)
            case "file":
                await self._send_file(data)
            case _:
                return None

    async def _send_text(self, data: Dict[str, any]):
        for connection in self.active_connections[data["chat_id"]].values():
            await connection.send_json(data)

    async def _send_file(self, chat_id: int, user_id: int, message: str):
        pass