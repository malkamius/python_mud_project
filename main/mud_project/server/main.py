import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

import signal
import sys

import asyncio
import logging
from ..server.protocols.telnet_protocol import TelnetProtocol

logger = logging.getLogger(__name__)


async def start_server(config, world_manager, game_loop, connection_manager):
    telnet_protocol = TelnetProtocol(world_manager, game_loop, connection_manager)

    host = config['server']['host']
    port = config['server']['port']
    
    def protocol_factory():
        return lambda reader, writer: telnet_protocol.handle_connection(reader, writer)

    
    server = await asyncio.start_server(
        protocol_factory(), host, port)
    
    addr = server.sockets[0].getsockname()
    logger.info(f'Serving on {addr}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError as e:
            print('Server cancelled')
        finally:
            server.close()
            #await game_loop.stop()

