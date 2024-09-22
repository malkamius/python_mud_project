from .base_connection import BaseConnection
import websockets
from typing import TYPE_CHECKING
from ..color import colorize
if TYPE_CHECKING:
    from ..connection_manager import ConnectionManager

class WebSocketConnection(BaseConnection):
    def __init__(self, websocket, connection_manager):
        super().__init__(connection_manager)
        self.websocket = websocket
        from ..connection_manager import ConnectionManager
        self.connection_manager : ConnectionManager = connection_manager
        
    async def handle_connection(self):
        try:
            await self.on_connect()
            
            async for message in self.websocket:
                if isinstance(message, bytes):
                    message = message.decode("UTF-8")
                await self.add_to_buffer(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.on_disconnect()
            await self.connection_manager.remove_connection(self)

    async def send(self, data):
        if isinstance(data, bytes):
            await self.websocket.send(data)
        else:
            try:
                data = colorize(data, False, False, False)
            except Exception as e:
                print(str(e))
            encoded_data = data.encode("UTF-8", errors='replace')
            await self.websocket.send(encoded_data)

    async def close(self):
        await self.websocket.close()

    def get_address(self):
        return self.websocket.remote_address