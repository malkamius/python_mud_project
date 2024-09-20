from time import struct_time
from typing import Dict

from .room_template import RoomTemplate
from .npc_template import NPCTemplate

class AreaTemplate:
    

    def __init__(self):
        self.name : str = ""
        self.credits : str = ""
        self.saved : bool = True
        self.info : str = ""
        self.vnum_start : int = 0
        self.vnum_end : int = 0
        self.builders : str = ""
        self.security : int = 60
        self.last_reset : struct_time

        self.room_templates : Dict[int, RoomTemplate] = {}
        self.npc_templates : Dict[int, NPCTemplate] = {}