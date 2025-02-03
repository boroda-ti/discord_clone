import asyncio
import websockets
import json
import datetime

async def send_message():
    uri = "ws://127.0.0.1:8000/api/chat/ws/chat?chat_id=0&user_id=0"  # URL вашего WebSocket сервера
    async with websockets.connect(uri) as websocket:
        message = {
            "chat_id": 0,
            "user_id": 0,
            "message": "Hello, FastAPI WebSocket!",
            "data_type": "text",
            "created_at": str(datetime.datetime.now(datetime.timezone.utc)),
            "updated_at": str(datetime.datetime.now(datetime.timezone.utc)),
        }
        await websocket.send(json.dumps(message))
        print("Message sent:", message)

        # Получаем ответ
        response = await websocket.recv()
        print("Response received:", response)

if __name__ == "__main__":
    asyncio.run(send_message())