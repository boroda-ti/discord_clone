from typing import Dict, List
from fastapi import WebSocket


class ChatSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket, List[int]]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, chat_ids: List[int]):
        self.active_connections[user_id] = [websocket, chat_ids]

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)