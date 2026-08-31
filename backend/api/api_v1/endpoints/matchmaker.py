from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import uuid
import json
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.waiting_queue: List[str] = []

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.waiting_queue:
            self.waiting_queue.remove(user_id)

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def find_match(self, user_id: str):
        if len(self.waiting_queue) > 0:
            partner_id = self.waiting_queue.pop(0)
            # Notify both
            room_id = str(uuid.uuid4())
            await self.send_personal_message({"type": "match_found", "partner_id": partner_id, "room_id": room_id, "role": "interviewer"}, user_id)
            await self.send_personal_message({"type": "match_found", "partner_id": user_id, "room_id": room_id, "role": "candidate"}, partner_id)
        else:
            self.waiting_queue.append(user_id)
            await self.send_personal_message({"type": "waiting_in_queue"}, user_id)

manager = ConnectionManager()

@router.websocket("/matchmaker/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "find_match":
                await manager.find_match(user_id)
            
            elif message["type"] == "chat":
                # Forward chat to partner in room (Simplified)
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
