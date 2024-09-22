from abc import ABC, abstractmethod
from uuid import uuid1
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..connection_manager import ConnectionManager

class BaseConnection(ABC):
    id : str

    def __init__(self, connection_manager):
        from ..protocols.telnet_handler import TelnetHandler
        self.telnet_handler : TelnetHandler = None
        self.connection_manager = connection_manager
        self.player = None
        self.is_authenticated = False
        self.id = uuid1()
        self.input_buffer = ""
        self.buffer_lock = asyncio.Lock()

    @abstractmethod
    async def handle_connection(self):
        """
        Main method to handle the connection. This should be implemented
        by each specific connection type to handle its own protocol.
        """
        pass

    @abstractmethod
    async def send(self, data):
        """
        Send data to the client. This should be implemented by each
        specific connection type to handle its own protocol.
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Close the connection. This should be implemented by each
        specific connection type to properly clean up resources.
        """
        pass

    @abstractmethod
    def get_address(self):
        """
        Get the address of the connected client. This should be implemented
        by each specific connection type to return the appropriate address.
        """
        pass

    async def authenticate(self, username, password):
        """
        Authenticate the player. This method can be overridden by specific
        connection types if they need custom authentication logic.
        """
        # Here you would typically check the username and password against your database
        # For now, we'll just set is_authenticated to True
        self.is_authenticated = True
        # You might also want to load or create a Player object here
        # self.player = await load_player(username)
        return self.is_authenticated

    async def add_to_buffer(self, data: str) -> bool:
        async with self.buffer_lock:
            data = data.replace('\r\n', '\n').replace('\n\r', '\n').replace('\r', '\n')
            if len(data) + len(self.input_buffer) > 400:
                await self.send("Are you writing a novel? Too much text, sorry.\r\n")
                await self.close()
                return False
            
            for char in data:
                if ord(char) in (8, 127):  # ASCII 8 or 127 (backspace or delete)
                    if self.input_buffer and self.input_buffer[-1] != '\n':  # If there are characters in the buffer
                        self.input_buffer = self.input_buffer[:-1]  # Remove the last character
                elif ord(char) in (13, 10):  # CR or LF
                    self.input_buffer += '\n'  # Add a newline character
                    if self.input_buffer.count('\n') > 40:
                        await self.send("Too many lines at once, sorry.\r\n")
                        await self.close()
                        return False
                elif ord(char) >= 32:  # Printable ASCII characters
                    self.input_buffer += char
            return True

    async def buffer_has_line(self) -> bool:
        return '\n' in self.input_buffer

    async def buffer_read_line(self) -> str:
        async with self.buffer_lock:
            data, self.input_buffer = self.input_buffer.split('\n', 1)
        return data

    async def on_connect(self):
        """
        Called when a new connection is established. This can be overridden
        to perform any necessary setup.
        """
        await self.send("Welcome to the MUD!\n")

    async def on_disconnect(self):
        """
        Called when the connection is closed. This can be overridden
        to perform any necessary cleanup.
        """
        if self.player:
            # Here you might want to save the player's state, remove them from the game world, etc.
            pass

    def get_id(self):
        return self.id