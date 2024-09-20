import asyncio
from ...server.connections.telnet_connection import TelnetConnection

class TelnetProtocol:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    async def handle_connection(self, reader, writer):
        telnet_connection = TelnetConnection(reader, writer, self.connection_manager)
        await self.connection_manager.add_connection(telnet_connection)
        
        try:
            await telnet_connection.handle_connection()
        except Exception as e:
            print(f"Error in telnet connection: {e}")
        finally:
            await self.connection_manager.remove_connection(telnet_connection)