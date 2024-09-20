from time import struct_time
from typing import Dict

from .room_template import RoomTemplate
from .npc_template import NPCTemplate

class AreaTemplate:
    name : str = ""
    credits : str = ""
    saved : bool = True
    info : str = ""
    vnum_start : int = 0
    vnum_end : int = 0
    builders : str = ""
    security : int = 60
    last_reset : struct_time

    room_templates : Dict[int, RoomTemplate] = {}
    npc_templates : Dict[int, NPCTemplate] = {}

    def __init__():
        pass