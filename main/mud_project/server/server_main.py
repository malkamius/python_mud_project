import sys
import os
import asyncio
import logging
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

import signal
import sys

import asyncio
import logging
from .protocols.telnet_protocol import TelnetProtocol

from .config import load_config
from .database.db_handler import DatabaseHandler
from .world.world_manager import WorldManager
from .game_loop import GameLoop
from .connection_manager import ConnectionManager
from .world.CrimsonStainedLands.world_manager import CrimsonStainedLandsWorldManager
from .commands import load_commands_from_folder

class GameServer:
    

    def __init__(self, shutdown_flag : asyncio.Event):
        self.connection_manager : ConnectionManager = None
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.shutdown_flag = shutdown_flag
        self.game_loaded = asyncio.Event()

    async def shutdown(self, loop, signal=None):
        """Cleanup tasks tied to the service's shutdown."""
        if signal:
            print(f"Received exit signal {signal.name}...")
        
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        print(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    async def launch(self):


        self.logger.info("Starting MUD server...")

        try:
            # Load configuration
            config = load_config()
            load_commands_from_folder(os.path.join("mud_project", "server", "character_commands"))

            async with DatabaseHandler(config['database']) as db_handler:
                game_loop = GameLoop(self.game_loaded)
                
                # Initialize connection manager
                connection_manager = ConnectionManager(game_loop)
                
                world_manager = CrimsonStainedLandsWorldManager(config['world'], db_handler)

                # Start the server
                server_task = asyncio.create_task(self.start_servers(config, connection_manager))

                # Initialize world
                start_time = time.time()
                await world_manager.load_templates()
                end_time = time.time()
                execution_time_ms = (end_time - start_time) * 1000
                print(f"Execution time: {execution_time_ms} milliseconds to load areas")
                
                start_time = time.time()

                for area_template in world_manager.area_templates.values():
                    for room_template in area_template.room_templates.values():
                        for exit in room_template.exits.values():
                            exit.Destination = world_manager.get_room(exit.DestinationVnum)
                            #await asyncio.sleep(0)
                end_time = time.time()
                execution_time_ms = (end_time - start_time) * 1000
                print(f"Execution time: {execution_time_ms} milliseconds to fix exits")
                
                #await world_manager.load_world_state()

                #reset areas
                
                self.game_loaded.set()
                # Initialize game loop
                

                
                game_loop_task = asyncio.create_task(game_loop.start(connection_manager, world_manager))

                # Wait for the shutdown flag to be set
                await self.shutdown_flag.wait()

                await game_loop.stop()

                await game_loop_task

                
                # Cancel the server task
                server_task.cancel()
                    
            try:
                await server_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            self.logger.exception(f"An error occurred in the main function: {e}")
        finally:
            self.logger.info("Shutting down...")
            await self.shutdown(asyncio.get_event_loop())

    async def start_servers(self, config, connection_manager):
        telnet_protocol = TelnetProtocol(connection_manager)

        host = config['server']['host']
        port = config['server']['port']
        
        def protocol_factory():
            return lambda reader, writer: telnet_protocol.handle_connection(reader, writer)

        
        server = await asyncio.start_server(
            protocol_factory(), host, port)
        
        addr = server.sockets[0].getsockname()
        self.logger.info(f'Serving on {addr}')

        async with server:
            try:
                await server.serve_forever()
            except asyncio.CancelledError as e:
                print('Server cancelled')
            finally:
                server.close()