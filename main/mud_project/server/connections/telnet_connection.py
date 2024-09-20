import asyncio
from .base_connection import BaseConnection
from ..protocols.telnet_handler import TelnetHandler
from ..color import colorize
class TelnetConnection(BaseConnection):


    def __init__(self, reader, writer, connection_manager):
        super().__init__(connection_manager)
        self.reader = reader
        self.writer = writer
        self.telnet_handler = TelnetHandler(self)
        self.address = writer.get_extra_info('peername')
        

    async def handle_connection(self):
        try:
            self.is_authenticated = True
            
            await self.telnet_handler.negotiate_options()
            while not self.writer.is_closing():
                data = await self.reader.read(1024)
                if not data:
                    break
                if not await self.telnet_handler.process_input(data):
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error handling telnet connection: {e}")
        finally:
            await self.close()
    
    async def send(self, data):
        if isinstance(data, bytes):
            self.writer.write(data)
        else:
            try:
                data = colorize(data)
            except Exception as e:
                print(str(e))
            encoded_data = data.encode(self.telnet_handler.char_set, errors='replace')
            
            # Check if the data ends with \r or \n
            if not encoded_data.endswith(b'\r') and not encoded_data.endswith(b'\n') and self.telnet_handler.eor:
                eor_command = b'\xff\xef'  # IAC (255) EOR (239)
                encoded_data += eor_command
            elif not encoded_data.endswith(b'\r') and not encoded_data.endswith(b'\n') and not self.telnet_handler.supress_go_ahead:
                sga_command = b'\xff\xf9'  # IAC (255) GoAhead (249)
                encoded_data += sga_command

            self.writer.write(encoded_data)
        await self.writer.drain()

    async def close(self):
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()
        await self.connection_manager.remove_connection(self)

    def get_address(self):
        return self.address