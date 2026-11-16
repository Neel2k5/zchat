from classes.connection_handler import ConnectionHandler
from asyncio import sleep

# Periordic cleanup of connections
async def periodic_cleanup(conn_handler:ConnectionHandler,interval_seconds: int = 30):
    while True:
        await sleep(interval_seconds)
        removed = await conn_handler.cleanup_stale_connections()
        if removed:
            print(f"[Cleanup] Removed {removed} stale connection(s)")