import asyncio
from typing import Dict, Callable
from ..connections.base_connection import BaseConnection
# Telnet protocol constants
IAC = bytes([255])
DONT = bytes([254])
DO = bytes([253])
WONT = bytes([252])
WILL = bytes([251])
SB = bytes([250])
SE = bytes([240])

# Telnet options
ECHO = bytes([1])
SUPRESS_GO_AHEAD = bytes([3])
TTYPE = bytes([24])
NAWS = bytes([31])
CHARSET = bytes([42])
MXP = bytes([91])
EOR = bytes([25])

class TelnetHandler:
    def __init__(self, connection : BaseConnection):
        self.connection = connection
        self.buffer = b''
        self.negotiation_table: Dict[bytes, Callable] = {
            ECHO: self.handle_echo,
            SUPRESS_GO_AHEAD: self.handle_supress_go_ahead,
            TTYPE: self.handle_ttype,
            NAWS: self.handle_naws,
            CHARSET: self.handle_charset,
            MXP: self.handle_mxp,
            EOR: self.handle_eor
        }
        self.will_ttype = False
        self.terminal_types = []
        self.char_set = "Windows-1252"
        self.eor = True
        self.supress_go_ahead = True
        self.echo = False

    async def process_input(self, data: bytes) -> bool:
        self.buffer += data
        if len(self.buffer) > 400 or len(self.connection.input_buffer) > 400:
            await self.connection.send("Are you writing a novel? Too much text, sorry.\r\n")
            return False
        
        while IAC in self.buffer:
            plain_text, self.buffer = self.buffer.split(IAC, 1)
            if plain_text:
                await self.handle_plain_text(plain_text.decode(self.char_set, errors='ignore'))
            
            if len(self.buffer) < 2:
                break
            
            command = self.buffer[0:1]
            option = self.buffer[1:2]
            self.buffer = self.buffer[2:]
            
            if command in (DO, DONT, WILL, WONT):
                await self.handle_negotiation(command, option)
            elif command == SB:
                await self.handle_subnegotiation(option)
        
        if len(self.buffer) > 0:
            await self.handle_plain_text(self.buffer.decode(self.char_set, errors='ignore'))
            self.buffer = b''
        return True

    async def handle_plain_text(self, text: str):
        await self.connection.add_to_buffer(text)

    async def handle_negotiation(self, command: bytes, option: bytes):
        if option in self.negotiation_table:
            await self.negotiation_table[option](command)
        else:
            if command == DO:
                await self.send(IAC + WONT + option)
            elif command == WILL:
                await self.send(IAC + DONT + option)

    async def handle_subnegotiation(self, option):
        if SE in self.buffer:
            subneg, self.buffer = self.buffer.split(SE, 1)
            #option = subneg[0:1]
            if option == TTYPE:
                await self.handle_ttype_subneg(subneg[1:], subneg[0])
            elif option == CHARSET:
                await self.handle_charset_subneg(subneg[1:], subneg[0])
        # If SE is not in buffer, wait for more data

    async def handle_echo(self, command: bytes):
        if command == WILL or command == DONT:
            self.echo = False
            #await self.send(IAC + DO + ECHO)
        #elif command == WONT:
            #await self.send(IAC + WILL + ECHO)
            #self.echo = True

    async def handle_supress_go_ahead(self, command: bytes):
        if command in (DO):
            self.supress_go_ahead = True
        else:
            self.supress_go_ahead = False

    async def handle_eor(self, command: bytes):
        if command in (DO):
            self.eor = True
        else:
            self.eor = False

    async def handle_ttype(self, command: bytes):
        if command == WILL and not self.will_ttype:
            self.will_ttype = True
            await self.send(IAC + SB + TTYPE + bytes([1]) + IAC + SE)

        elif command == WONT:
            await self.send(IAC + DONT + TTYPE)

    async def handle_ttype_subneg(self, data: bytes, option):
        terminal_type = data.decode('ascii', errors='ignore')
        
        if not terminal_type in self.terminal_types:
            print(f"Client terminal type: {terminal_type}")
            self.terminal_types.append(terminal_type)
            await self.send(IAC + SB + TTYPE + bytes([1]) + IAC + SE)

        # Handle the terminal type information as needed

    async def handle_naws(self, command: bytes):
        if command == WILL:
            await self.send(IAC + DO + NAWS)
        else:
            await self.send(IAC + DONT + NAWS)

    async def handle_charset(self, command: bytes):
        if command == WILL:
            # Request the supported character sets
            await self.send(IAC + SB + CHARSET + bytes([1]) + b';UTF-8;Windows-1252' + IAC + SE)
        else:
            await self.send(IAC + DONT + CHARSET)

    async def handle_charset_subneg(self, data: bytes, option):
        charset_data = data.decode('ascii', errors='ignore')
        print(f"Client charset negotiation: {charset_data}")

        if charset_data == "UTF-8" and option == 2:
            self.char_set = charset_data
        #    await self.send(IAC + SB + CHARSET + bytes([1]) + charset_data.encode('ascii') + IAC + SE)
            
        # Handle the charset negotiation as per RFC 2066
        # This might involve parsing the accepted charset and setting it for the connection

    async def handle_mxp(self, command: bytes):
        #if command == WILL:
        #    await self.send(IAC + DO + MXP)
        #else:
        await self.send(IAC + DONT + MXP)

    async def send(self, data: bytes):
        await self.connection.send(data)

    async def negotiate_options(self):
        # Initiate option negotiations
        
        await self.send(IAC + DO + CHARSET)
        await self.send(IAC + DO + TTYPE)
        await self.send(IAC + WILL + EOR)
        await self.send(IAC + DO + ECHO)
        await self.send(IAC + WILL + SUPRESS_GO_AHEAD)
        #await self.send(IAC + DO + NAWS)
        #await self.send(IAC + WILL + MXP)