import asyncio
import websockets
import json
import datetime

async def send_message():
    uri = "ws://127.0.0.1:8000/ws/chat" #"ws://127.0.0.1:8000/api/chat/ws/chat?chat_id=0&user_id=0"  # URL вашего WebSocket сервера
    async with websockets.connect(uri) as websocket:
        user_id = int(input("USer_id: "))

        message = {
            "user_id": user_id,
        }
        await websocket.send(json.dumps(message))

        print("Connected to WebSocket server. Type your message and press Enter.")
        while True:
            msg = input("You: ")
            message = {
            "chat_id": 0,
            "user_id": user_id,
            "message": msg,
            "data_type": "text",
            # "created_at": str(datetime.datetime.now(datetime.timezone.utc)),
            # "updated_at": str(datetime.datetime.now(datetime.timezone.utc)),
            }

            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            print(f"Received: {response}")

    
if __name__ == "__main__":
    asyncio.run(send_message())