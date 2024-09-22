from typing import Dict, Tuple, Optional
import json
import os
from logging import getLogger

from .room_template import RoomTemplate
from .area_template import AreaTemplate
from .npc_template import NPCTemplate

class WorldManager:
    def __init__(self, configWorld, db_handler):
        self.logger = getLogger(__name__)
        self.area_templates: Dict[str, AreaTemplate] = {}
        self.room_templates: Dict[int, RoomTemplate] = {}
        self.npc_templates: Dict[int, NPCTemplate] = {}
        #self.load_templates()

    async def load_templates(self):
        # Load area templates
        area_template_path = 'mud_project/server/data/world/area_templates.json'
        if os.path.exists(area_template_path):
            with open(area_template_path, 'r') as f:
                self.area_templates = json.load(f)

        # Load room templates
        room_template_path = 'mud_project/server/data/world/room_templates'
        for filename in os.listdir(room_template_path):
            if filename.endswith('.json'):
                with open(os.path.join(room_template_path, filename), 'r') as f:
                    room_data = json.load(f)
                    for template in room_data['room_templates']:
                        self.room_templates[template['template_id']] = RoomTemplate.from_json(template)
    
    # def get_room(self, id : str) -> Optional[RoomInstance]:
    #     return self.room_instances.get(id, self.room_instances.get(f"0_{id}"))
    def get_room(self, id : int) -> Optional[RoomTemplate]:
         return self.room_templates.get(id)
    
    def get_or_create_room(self, area_id: str, coordinates: Tuple[int, int, int]):
        if area_id not in self.area_instances:
            raise ValueError(f"No area instance found with id: {area_id}")

        area = self.area_instances[area_id]
        room = area.get_room(coordinates)
        if room:
            return room
        
        room_type = self.choose_room_type(area, coordinates)
        return area.generate_room(room_type, coordinates)

    def get_room_template(self, template_id: str) -> Optional[RoomTemplate]:
        return self.room_templates.get(template_id)

    def get_area_template(self, template_id: str) -> Optional[Dict]:
        return self.area_templates.get(template_id)