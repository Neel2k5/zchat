from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from classes.connection_handler import ConnectionHandler
from asyncio import create_task
from contextlib import asynccontextmanager
from handlers.cleanup_handler import *


@asynccontextmanager
async def con_lifespan(app:FastAPI):
    clean_task = create_task(periodic_cleanup(conn_handler,30))
    yield
    clean_task.cancel()

app = FastAPI(title="Zchat", description="A simple websockets based chat server",lifespan=con_lifespan)

conn_handler = ConnectionHandler()

@app.get("/test")
def test():
    return "running"


@app.websocket("/ws")
async def wscon(websocket: WebSocket):
    con_id = await conn_handler.connect(websocket)
    try:
        await conn_handler.send_personal_message(f'{con_id}<<\nConnected to the server\nid:[{con_id}]\n{'='*50}\n','SERVER')
        while True:
            await conn_handler.conn_tick(con_id=con_id,websocket=websocket)

    except WebSocketDisconnect:
        conn_handler.remove_con(con_id)

