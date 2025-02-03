import flet as ft

from services.sockets.core import ChatSocketClient


async def ChatView(router):
    ws_client = ChatSocketClient("ws://localhost:8000/api/chat/ws/chat")

    async def send_message(e: ft.ControlEvent):
        await ws_client.send_message(8, input_field.value)
        chat_box.controls.append(ft.Text(f"You: {input_field.value}"))
        e.page.update()

    chat_box = ft.Column()
    input_field = ft.TextField(label="Message")
    send_button = ft.ElevatedButton("Send", on_click=send_message)

    content = ft.Column(
        controls = [
            ft.Box
        ]
    )
    
    return content


async def home_page(page: ft.Page):
    ws_client = ChatSocketClient("ws://localhost:8000/ws/chat")

    async def send_message(e):
        await ws_client.send_message(8, input_field.value)
        chat_box.controls.append(ft.Text(f"You: {input_field.value}"))
        page.update()

    chat_box = ft.Column()
    input_field = ft.TextField(label="Message")
    send_button = ft.ElevatedButton("Send", on_click=send_message)

    page.add(chat_box, input_field, send_button)