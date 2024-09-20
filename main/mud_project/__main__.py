import sys
import os
import signal
import platform
import asyncio
import logging
import time
import aiosqlite

from concurrent.futures import ThreadPoolExecutor

import aiosqlite.context

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)


from .server.main import start_server
from .server.config import load_config
from .server.database.db_handler import DatabaseHandler
from .server.world.world_manager import WorldManager
from .server.game_loop import GameLoop
from .server.connection_manager import ConnectionManager
from .server.world.CrimsonStainedLands.world_manager import CrimsonStainedLandsWorldManager
from .server.commands import load_commands_from_folder
shutdown_flag = asyncio.Event()
connection_manager : ConnectionManager = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    logger.warning(f"Received signal {sig}: initiating shutdown")
        
    shutdown_flag.set()

async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        print(f"Received exit signal {signal.name}...")
    
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for task in tasks:
        task.cancel()

    print(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():


    logger.info("Starting MUD server...")

    try:
        # Load configuration
        config = load_config()
        load_commands_from_folder(os.path.join("mud_project", "server", "character_commands"))

        async with DatabaseHandler(config['database']) as db_handler:
            
            # Initialize world
            start_time = time.time()
            world_manager = CrimsonStainedLandsWorldManager(config['world'], db_handler)
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            print(f"Execution time: {execution_time_ms} milliseconds to load areas")
            
            start_time = time.time()
            
            for area_template in world_manager.area_templates.values():
                for room_template in area_template.room_templates.values():
                    for exit in room_template.exits.values():
                        exit.Destination = world_manager.get_room(exit.DestinationVnum)
            
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            print(f"Execution time: {execution_time_ms} milliseconds to fix exits")
            
            # # Instantiate all CSL Areas
            # for area_template_id in world_manager.area_templates.keys():
            #     world_manager.create_area_instance(area_template_id)
            
        
            #await world_manager.load_world_state()

            
            # Initialize game loop
            game_loop = GameLoop(world_manager)

            # Initialize connection manager
            connection_manager = ConnectionManager(game_loop)
            
            game_loop.connection_manager = connection_manager

            # Start the server
            server_task = asyncio.create_task(start_server(config, world_manager, game_loop, connection_manager))

            game_loop_task = asyncio.create_task(game_loop.start())

            # Wait for the shutdown flag to be set
            await shutdown_flag.wait()

            await game_loop.stop()

            await game_loop_task

            
            # Cancel the server task
            server_task.cancel()
                
        try:
            await server_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        logger.exception(f"An error occurred in the main function: {e}")
    finally:
        logger.info("Shutting down...")
        await shutdown(asyncio.get_event_loop())

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor = ThreadPoolExecutor(max_workers=10)
    loop.set_default_executor(executor)
    # Setup signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        if platform.system() != 'Windows':
            # Unix-like systems
            loop.add_signal_handler(sig, signal_handler, sig, None)
        else:
            # Windows
            signal.signal(sig, signal_handler)
        
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt . . .")
        shutdown_flag.set()
    finally:
        logging.info("Cleaning up . . .")
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        executor.shutdown(wait=True, cancel_futures=True)
        logging.info("Exiting . . .")
    