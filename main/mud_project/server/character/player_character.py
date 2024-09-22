from .character import Character as CharacterBase, CharacterAttributes
from ..connections.base_connection import BaseConnection
import asyncio
from enum import Enum

class PlayerCharacterStates(Enum):
    Disconnected = 0
    Connected = 1
    GetName = 2
    Playing = 3

class PlayerCharacter(CharacterBase):

    def __init__(self):
        super().__init__()
        self.State = PlayerCharacterStates.Connected
        self.PasswordHash : str
        self.Connection : BaseConnection
        self.State : PlayerCharacterStates
        self.OutBuffer : str = ""
        self.InBuffer : str = ""
        self.NoCommand : bool = True
        self.SentPromp : bool = False
        

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