import re
from ..area_template import AreaTemplate
import xml.etree.ElementTree as ET
from ..room_template import RoomTemplate
from typing import Dict

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
    filepath : str
    
    def __init__(self, world_manager, filepath : str, header_only : bool = False):
        if header_only == False:
            self.filepath = filepath
            tree = ET.parse(filepath)

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
                if world_manager:
                    world_manager.add_template(room)