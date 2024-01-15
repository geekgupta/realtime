@router.websocket("/ws")
async def connect(websocket : WebSocket):
    await websocket.accept()
    print( await websocket.receive_text())
    while True:
      data = await websocket.receive_text()
      await websocket.send_text(f"Message text was: {data}")
    
# connection = []
# @app.websocket("/ws/px")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")



class WebSocketManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.connections[user_id] = websocket

        try:
            while True:
                data = await websocket.receive_text()
                await self.send_message(user_id, data)
        except:
            del self.connections[user_id]

    async def send_message(self, sender_id: str, message: str):
        for user_id, connection in self.connections.items():
            if user_id == sender_id:
                await connection.send_text(f"User {sender_id}: {message}")
                
    async def broadcast(self, sender_id: str, recipient_id: str, data: bytes):
        for user_id, connection in self.connections.items():
            if user_id == sender_id or user_id == recipient_id:
                # await connection.send_bytes(data)
                await connection.send_text(f"User {sender_id}: {connection.receive_text()}")

manager = WebSocketManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    print("*******" , user_id)
    await manager.connect(websocket, user_id) 
    
    
    
class WebSocketManager2:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        try:
            while True:
                data = await websocket.receive_bytes()
                await self.broadcast(user_id, data)
        except:
            del self.active_connections[user_id]

    async def broadcast(self, sender_id: str, data: bytes):
        for user_id, connection in self.active_connections.items():
            if user_id == sender_id:
                await connection.send_bytes(data)

chat_manager = WebSocketManager2()