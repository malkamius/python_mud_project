import sys
import os
import signal
import platform
import asyncio
import logging

from concurrent.futures import ThreadPoolExecutor
from .server.server_main import GameServer

shutdown_flag = asyncio.Event()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def signal_handler(sig, frame):
    logger.warning(f"Received signal {sig}: initiating shutdown")
        
    shutdown_flag.set()

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
    server = GameServer(shutdown_flag)
    try:
        loop.run_until_complete(server.launch())
    except KeyboardInterrupt:
        logging.info("Keyboard Interrupt . . .")
        shutdown_flag.set()
    finally:
        logging.info("Cleaning up . . .")
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        executor.shutdown(wait=True, cancel_futures=True)
        logging.info("Exiting . . .")
    