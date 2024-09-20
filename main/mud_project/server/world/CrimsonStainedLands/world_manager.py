from typing import Dict, Tuple, Optional
import json
import os
import time
from ..area_instance import AreaInstance
from ..room_template import RoomTemplate
from .area_template import CSLAreaTemplate
from ..world_manager import WorldManager
from ..room_instance import RoomInstance

class CrimsonStainedLandsWorldManager(WorldManager):
    def __init__(self, configWorld, db_handler):
        super().__init__(configWorld, db_handler)
        #self.area_templates: Dict[str, CSLAreaTemplate] = {}
        #self.room_templates: Dict[str, RoomTemplate] = {}
        self.load_templates()
        
    def add_template(self, obj):
        if isinstance(obj, RoomTemplate):
            self.room_templates[obj.template_id] = obj

    def load_templates(self):
        # Load area templates
        areas_path = '../../../CSLData/areas'
        for filename in os.listdir(areas_path):
            if filename.endswith('_Programs.xml') == False and filename.endswith('.xml'):
                area_path = os.path.join(areas_path, filename)
                area = CSLAreaTemplate(self, area_path)
                self.area_templates[area.name] = area
                self.logger.info(f"Loaded {area.name}")

    def create_area_instance(self, template_id: str) -> AreaInstance:
        if template_id not in self.area_templates:
            raise ValueError(f"No area template found with id: {template_id}")
        template = self.area_templates[template_id]
        new_area = AreaInstance(template)
        
        self.generate_area_rooms(new_area, None)
        
        new_area.complete_generation()
        
        self.area_instances[f"0_{template_id}"] = new_area
        return new_area

    def generate_area_rooms(self, area: AreaInstance, template: Dict):
        for room_template in self.room_templates.values():
            new_room = RoomInstance(room_template, area)
            
            new_room.id = f"0_{room_template.template_id}"
            if not new_room.id in self.room_instances.keys():
                self.room_instances[new_room.id] = new_room
                area.add_room(new_room)

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