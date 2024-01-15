import uvicorn
from fastapi import APIRouter 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, APIRouter , WebSocket 
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os 

app = FastAPI()

templates = Jinja2Templates(directory="template")

@app.get("/hello/", response_class=HTMLResponse)
async def hello(request: Request):
    return templates.TemplateResponse("indx.html", {"request": request})

router = APIRouter()

@app.get("/")
async def index(request : Request):
    return templates.TemplateResponse("index2.html" , {"request": request})



class ChatManager:
    def __init__(self):
        self.active_connections = {}
        self.group_connections = {}

    async def connect_to_private_chat(self, websocket: WebSocket, user_id: str, recipient_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        try:
            while True:
                data = await websocket.receive_text()
                await self.send_private_message(user_id, recipient_id, data)
        except:
            del self.active_connections[user_id]

    async def connect_to_group_chat(self, websocket: WebSocket, user_id: str, group_id: str):
        await websocket.accept()
        if group_id not in self.group_connections:
            self.group_connections[group_id] = []
        self.group_connections[group_id].append(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await self.send_group_message(group_id, data)
        except:
            self.group_connections[group_id].remove(websocket)

    async def send_private_message(self, sender_id: str, recipient_id: str, message: str):
        recipient_connection = self.active_connections.get(recipient_id)
        if recipient_connection:
            await recipient_connection.send_text(f"Private message from {sender_id}: {message}")

    async def send_group_message(self, group_id: str, message: str):
        group_connections = self.group_connections.get(group_id)
        if group_connections:
            for connection in group_connections:
                await connection.send_text(f"Group message: {message}")

chat_manager = ChatManager()

@app.websocket("/private/{user_id}/{recipient_id}")
async def private_chat(websocket: WebSocket, user_id: str, recipient_id: str):
    await chat_manager.connect_to_private_chat(websocket, user_id, recipient_id)

@app.websocket("/group/{group_id}/{user_id}")
async def group_chat(websocket: WebSocket, group_id: str, user_id: str):
    await chat_manager.connect_to_group_chat(websocket, user_id, group_id)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
