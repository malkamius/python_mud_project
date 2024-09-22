import re
from ..area_template import AreaTemplate
import xml.etree.ElementTree as ET
from ..room_template import RoomTemplate
from typing import Dict
import asyncio
import aiofiles

def clean_text(text):
    if text is None:
        return None
    def replace_func(match):
        newline = match.group(1)
        whitespace = match.group(2)

        return f"{newline}"  # Keep whitespace, remove period
       
    # Remove leading spaces and tabs after newlines
    return re.sub(r'(\n|\r)\s+', replace_func, text)

class CSLAreaTemplate(AreaTemplate):
    
    def __init__(self, world_manager, filepath : str):
        super().__init__()
        self.filepath : str = filepath
        self.world_manager = world_manager
            
    
    async def load(self):
        async with aiofiles.open(self.filepath, mode='r', encoding='utf-8') as f:
            content = await f.read()
    
        # Parse the XML content
        tree = ET.fromstring(content)

        areadata = tree.find("AreaData")

        self.name = areadata.get("Name") or areadata.findtext("Name")

        for roomdata in tree.findall("Rooms/Room"):
            room = RoomTemplate(None)
            
            room.template_id = int(roomdata.findtext("VNum"))
            room.name = roomdata.findtext("Name")
            room.description = clean_text(roomdata.findtext("Description"))
            room.exits = {}
            from ..room_template import DirectionEnum, ExitData

            for exitnode in roomdata.findall("Exits/Exit"):
                direction = DirectionEnum[exitnode.findtext("Direction")]
                exitdata = ExitData()
                exitdata.DestinationVnum = int(exitnode.findtext("Destination"))
                room.exits[direction] = exitdata
                
            self.room_templates[room.template_id] = room
            if self.world_manager:
                await self.world_manager.add_template(room)