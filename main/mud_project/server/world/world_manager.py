from typing import Dict, Tuple, Optional
import json
import os
from logging import getLogger

from .area_instance import AreaInstance
from .room_template import RoomTemplate
from .room_instance import RoomInstance
from .area_template import AreaTemplate
class WorldManager:
    def __init__(self, configWorld, db_handler):
        self.logger = getLogger(__name__)
        self.area_templates: Dict[str, AreaTemplate] = {}
        self.room_templates: Dict[int, RoomTemplate] = {}
        self.area_instances: Dict[str, AreaInstance] = {}
        self.room_instances: Dict[str, RoomInstance] = {}

        self.load_templates()

    def load_templates(self):
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

    def create_area_instance(self, template_id: str) -> AreaInstance:
        if template_id not in self.area_templates:
            raise ValueError(f"No area template found with id: {template_id}")

        template = self.area_templates[template_id]
        new_area = AreaInstance(template_id, template['name'])
        
        # Generate initial room
        entry_room_type = template.get('entry_room_type', 'default_room')
        entry_coordinates = (0, 0, 0)
        new_area.generate_room(entry_room_type, entry_coordinates)
        
        # Generate additional rooms based on template specifications
        self.generate_area_rooms(new_area, template)
        
        new_area.complete_generation()
        self.area_instances[new_area.name] = new_area
        return new_area

    def generate_area_rooms(self, area: AreaInstance, template: Dict):
        # This method would contain the logic for generating rooms based on the area template
        # For example, it might create a certain number of rooms, or rooms with specific properties
        pass
    
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

    def choose_room_type(self, area: AreaInstance, coordinates: Tuple[int, int, int]) -> str:
        # This method would contain the logic for choosing an appropriate room type
        # based on the area, coordinates, and possibly adjacent rooms
        # For now, we'll just return a default room type
        return 'default_room'

    def get_area_instance(self, area_id: str) -> Optional[AreaInstance]:
        return self.area_instances.get(area_id)

    def get_all_area_instances(self) -> Dict[str, AreaInstance]:
        return self.area_instances

    def save_world_state(self, filename: str):
        world_state = {
            'area_instances': {name: area.to_dict() for name, area in self.area_instances.items()}
        }
        with open(filename, 'w') as f:
            json.dump(world_state, f, indent=2)

    def load_world_state(self, filename: str):
        with open(filename, 'r') as f:
            world_state = json.load(f)
        
        self.area_instances = {}
        for name, area_data in world_state['area_instances'].items():
            self.area_instances[name] = AreaInstance.from_dict(area_data)

    def delete_area_instance(self, area_id: str):
        if area_id in self.area_instances:
            del self.area_instances[area_id]

    def get_room_template(self, template_id: str) -> Optional[RoomTemplate]:
        return self.room_templates.get(template_id)

    def get_area_template(self, template_id: str) -> Optional[Dict]:
        return self.area_templates.get(template_id)