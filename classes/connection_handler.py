from fastapi import WebSocket
from models.connection_model import ConnectionModel
from fastapi.websockets import WebSocketState

class ConnectionHandler:
    def __init__(self):
        self.connections: dict[str, ConnectionModel] = {}

    async def connect(self, socket: WebSocket) -> str:
        await socket.accept()
        return self.add_con(socket)

    def add_con(self, socket: WebSocket) -> str:
        cm = ConnectionModel(socket=socket)
        con_id = cm.id
        self.connections[con_id] = cm
        return con_id

    def remove_con(self, con_id: str) -> None:
        self.connections.pop(con_id, None)


    async def conn_tick(self,con_id:str,websocket:WebSocket):
        data = await websocket.receive_text()
        if "<<<" in data:
            await self.broadcast(data, sender_con_id=con_id)
        elif "<<" in data:
            await self.send_personal_message(data, sender_con_id=con_id)
        else:
            await self.broadcast(data, sender_con_id=con_id)

    async def send_personal_message(self, message: str, sender_con_id: str) -> None:
        target_id, text = self.process_msg(message, delimiter="<<")
        cm = self.connections.get(target_id)
        if cm:
            try:
                await cm.socket.send_text(f"[{sender_con_id}] {text}")
            except:
                self.remove_con(cm.id)

    async def broadcast(self, message: str, sender_con_id: str | None = None) -> None:
        disconnected_ids = []
        if "<<<" in message:
            raw_ids, text = self.process_msg(message, delimiter="<<<")
            broadcast_set = [cid.strip() for cid in raw_ids.split(",") if cid.strip()]
        else:
            broadcast_set = list(self.connections.keys())
            text = message

        formatted_msg = f"[{sender_con_id}] {text}" if sender_con_id else text

        for con_id in broadcast_set:
            cm = self.connections.get(con_id)
            if cm:
                try:
                    await cm.socket.send_text(formatted_msg)
                except Exception:
                    disconnected_ids.append(cm.id)

        for con_id in disconnected_ids:
            self.remove_con(con_id)


    async def cleanup_stale_connections(self) -> int:
        dead_ids = []
        for con_id, cm in list(self.connections.items()):
            if cm.socket.client_state != WebSocketState.CONNECTED:
                dead_ids.append(con_id)
                continue
            try:
                await cm.socket.send_text("[PING]")  # ping
            except Exception:
                dead_ids.append(con_id)
        for con_id in dead_ids:
            self.remove_con(con_id)
        return len(dead_ids)

    def process_msg(self, message: str, delimiter: str = "<<") -> list[str]:
        processed = message.split(delimiter, 1)
        if len(processed) <= 1:
            return ["", message]
        return [processed[0], processed[1]]
    
