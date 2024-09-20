from .character import Character as CharacterBase
from ..connections.base_connection import BaseConnection
import asyncio
from enum import Enum

class PlayerCharacterStates(Enum):
    Disconnected = 0
    Connected = 1
    GetName = 2
    Playing = 3

class PlayerCharacter(CharacterBase):
    PasswordHash : str
    Connection : BaseConnection
    State : PlayerCharacterStates
    OutBuffer : str = ""
    InBuffer : str = ""

    def __init__(self):
        self.State = PlayerCharacterStates.Connected

    def send(self, message: str):
        if self.Connection != None:
            self.OutBuffer += message
        
        # # Get the current event loop
        # loop = asyncio.get_event_loop()
        
        # # If we're already in an event loop, we can create a task
        # if loop.is_running():
        #     loop.create_task(self.Connection.send(message))
        # else:
        #     # If we're not in an event loop, we need to run the coroutine
        #     loop.run_until_complete(self.Connection.send(message))