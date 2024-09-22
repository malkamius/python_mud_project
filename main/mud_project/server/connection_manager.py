import asyncio
from ..server.connections.base_connection import BaseConnection
from ..server.connections.telnet_connection import TelnetConnection
from ..server.connections.websocket_connection import WebSocketConnection

from typing import List

class ConnectionManager:
    connections : List
    
    def __init__(self, game_loop):
        self.connections : List[BaseConnection] = []
        self.game_loop = game_loop
        game_loop.connection_manager = self

    async def handle_new_connection(self, reader, writer):
        connection = TelnetConnection(reader, writer, self)
        await self.add_connection(connection)
        asyncio.create_task(connection.handle_connection())

    
    async def handle_new_websocket_connection(self, websocket, path):
        connection = WebSocketConnection(websocket, self)
        await self.add_connection(connection)
        await connection.handle_connection()


    async def add_connection(self, connection):
        self.connections.append(connection)
        await self.game_loop.on_player_connect(connection)

    async def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
            self.game_loop.on_player_disconnect(connection)

    async def broadcast(self, message, exclude=None):
        for connection in self.connections:
            if connection != exclude:
                await connection.send(message)

    def get_connection_count(self):
        return len(self.connections)

    async def close_all_connections(self):
        close_tasks = [connection.close() for connection in self.connections]
        await asyncio.gather(*close_tasks)
        self.connections.clear()
    
    async def __aenter__(self):
        #await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all_connections()