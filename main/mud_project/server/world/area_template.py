from datetime import datetime
from typing import Dict, List

from .room_template import RoomTemplate
from .npc_template import NPCTemplate
from .reset_data import ResetData

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
        self.last_reset : datetime = None

        self.room_templates : Dict[int, RoomTemplate] = {}
        self.npc_templates : Dict[int, NPCTemplate] = {}
        self.resets : List[ResetData] = []