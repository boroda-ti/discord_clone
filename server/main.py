import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router
from text_chat.router import ws_router, api_router


app = FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(api_router, prefix="/api/chat", tags=["Chat"])
app.include_router(ws_router, prefix="/ws", tags=["Chat websocket"])

@app.get("/")
async def root():
    return {"message": "Chat server is running!"}