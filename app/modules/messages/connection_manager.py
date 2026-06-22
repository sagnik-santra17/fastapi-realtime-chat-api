# Global imports
from fastapi import WebSocket


# --------- Connection Manager Class -------- #
class ConnectionManager:
    def __init__(self):
        # This dictionary tracks active connections.
        # Key = room_id (int), Value = list of active WebSocket lines
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, room_id: int, websocket: WebSocket) -> None:
        # Opening the line to user's browser
        await websocket.accept()
        # If the room list doesn't exist in memory yet, create it
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        # Add this specific user's connection line to the room list
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket) -> None:
        # Remove the user's connection line from the room list
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            # If nobody is left in the room, delete the room from the dictionary
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, room_id: int, message: str) -> None:
        # If the room exists, loop through every active user line and send the message
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

manager = ConnectionManager()
