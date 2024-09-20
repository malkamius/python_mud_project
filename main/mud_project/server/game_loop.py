import asyncio
import time
import re
import asyncio

from typing import List
from ..server.connection_manager import ConnectionManager
from ..server.connections.base_connection import BaseConnection
from ..server.character.player_character import PlayerCharacter, PlayerCharacterStates
from .world.world_manager import WorldManager
from .commands import commands
from .character_commands.information.look import look as do_look

class GameLoop:
    

    def __init__(self, game_loaded : asyncio.Event, tick_rate=4):
        self.connection_manager : ConnectionManager = None
        self.world_manager : WorldManager = None
        self.game_loaded = game_loaded
        
        self.tick_rate = tick_rate
        self.tick_interval = 1.0 / tick_rate
        self.is_running = False
        self.players: List[PlayerCharacter] = []
        self.last_tick_time = 0

    async def process_input(self, character : PlayerCharacter):
        line = None
        if await character.Connection.buffer_has_line():
            line = await character.Connection.buffer_read_line()
            character.NoCommand = False
            await self.handle_command(character, line)
    
    async def handle_command(self, character : PlayerCharacter, line : str):
        if(character.State == PlayerCharacterStates.Playing):
            if line.strip() == "":
                character.send("\r\n")
            elif " " in line:
                lookupname, args = line.split(" ", 1)
                lookupname = lookupname.lower()
            else:
                args = ""
                lookupname = line.lower()
            
            for command in commands:
                if len(command.name) >= len(lookupname) and command.name.lower().startswith(lookupname):
                    command.func(character, args)
                    return
            character.send("Huh?\r\n")
        else:
            character.send(f"You sent the line: {line}\r\n")

    async def start(self, connection_manager : ConnectionManager, world_manager : WorldManager):
        self.connection_manager = connection_manager
        self.world_manager = world_manager
        self.is_running = True
        self.bob_count = 1

        while self.is_running:
            start_time = time.time()
            
            await self.update()
            
            elapsed_time = time.time() - start_time
            if elapsed_time < self.tick_interval:
                await asyncio.sleep(self.tick_interval - elapsed_time)

            if len(self.players) == 0: 
                continue

            for character in self.players:
                character.NoCommand = True
                try:
                    await self.process_input(character)
                except:
                    pass

            for character in self.players:
                try:
                    if character.State == PlayerCharacterStates.GetName:
                        character.name = f"Bob{self.bob_count if self.bob_count > 1 else ""}"
                        self.bob_count += 1
                        
                        character.send(f"\r\nNevermind, your name is now {character.name}\r\nProgressing to Playing state\r\n欢迎来到多用户地下城\r\n")
                        defaultroom = self.world_manager.get_room(3001)
                        defaultroom.send(f"{character.name} has awakened from their slumber.")
                        character.CharacterToRoom(defaultroom)
                        character.State = PlayerCharacterStates.Playing
                        do_look(character, "")
                    #else:
                    #    character.send("PULSE\r\n")
                except Exception as ex:
                    print(f"Error {ex}")
            for character in self.players:
                if len(character.OutBuffer) > 0 and character.Connection != None:
                    try:
                        text = re.sub(r'(?<!\r)\n', '\r\n', character.OutBuffer)

                        #if character.NoCommand == False and character.SentPromp == True and not text.startswith("\r\n") and not text.startswith("\n"):
                        #    text = "\r\n" + text
                        if character.State == PlayerCharacterStates.Playing and not text.endswith("\n"):
                            text = text + "\r\n"
                        if character.State == PlayerCharacterStates.Playing:
                            if not text.endswith("\r\n\r\n") and text != "\r\n":
                                text = text + "\r\n"
                            text = text + "<100%hp 100%m 100%mv> "
                            character.SentPromp = True
                        await character.Connection.send(text)
                    except:
                        print("Failed to send out buffer")
                    finally:
                        character.OutBuffer = ""
        try:
            if(self.connection_manager != None):
                for connection in self.connection_manager.connections:
                    await connection.send("\r\nShutting down NOW!!!")
                    
        except:
            print("Failed to send shutdown message")
        await self.connection_manager.close_all_connections()
    async def stop(self):
        self.is_running = False

    async def update(self):
        current_time = time.time()
        delta_time = current_time - self.last_tick_time
        self.last_tick_time = current_time

        # Update game world
        #await self.world_manager.update(delta_time)

        # Process player actions
        for player in self.players:
            await self.process_player_actions(player)

        # Update NPCs, monsters, etc.
        await self.update_npcs()

        # Handle scheduled events
        await self.handle_scheduled_events()

        # Send updates to players
        await self.send_updates_to_players()

    async def process_player_actions(self, player: PlayerCharacter):
        # Process any queued actions for the player
        # This could include movement, combat actions, etc.
        pass

    async def update_npcs(self):
        # Update NPC behaviors, movement, etc.
        pass

    async def handle_scheduled_events(self):
        # Process any time-based events (respawns, weather changes, etc.)
        pass

    async def send_updates_to_players(self):
        # Send relevant updates to each player (nearby events, status changes, etc.)
        for player in self.players:
            await self.send_player_update(player)

    async def send_player_update(self, player: PlayerCharacter):
        # Compose and send an update specific to this player
        update = self.compose_player_update(player)
        #await player.Connection.send(update)

    def compose_player_update(self, player: PlayerCharacter) -> str:
        # Compose an update message for the player
        # This could include nearby events, status changes, etc.
        return "Game world update placeholder"

    def add_player(self, player: PlayerCharacter):
        self.players.append(player)

    def remove_player(self, player: PlayerCharacter):
        if player in self.players:
            self.players.remove(player)

    async def on_player_connect(self, connection: BaseConnection):
        await self.game_loaded.wait()
        player = PlayerCharacter()
        player.Connection = connection
        player.State = PlayerCharacterStates.Connected
        self.add_player(player)
        # Perform any necessary setup for the newly connected player
        welcome_message = "Welcome to the MUD!\r\nEnter your name: "
        
        
        # Send the welcome message followed by the EOR command
        await connection.send(welcome_message)
        #await connection.send(welcome_message)
        player.State = PlayerCharacterStates.GetName

    def on_player_disconnect(self, connection: BaseConnection):
        player = self.find_player_by_connection(connection)
        if player:
            self.remove_player(player)
        # Perform any necessary cleanup for the disconnected player

    def find_player_by_connection(self, connection: BaseConnection) -> PlayerCharacter:
        for player in self.players:
            if player.Connection == connection:
                return player
        return None

    def get_player_count(self) -> int:
        return len(self.players)

    async def broadcast_message(self, message: str, exclude: List[PlayerCharacter] = None):
        for player in self.players:
            if exclude and player in exclude:
                continue
            await player.Connection.send(message)