import json
import os
from typing import Dict, List, Any
from room_template import RoomTemplate
from area_template import AreaTemplate

class WorldLoader:
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        self.area_templates: Dict[str, AreaTemplate] = {}
        self.room_templates: Dict[str, RoomTemplate] = {}

    def load_all(self):
        self.load_area_templates()
        self.load_room_templates()

    def load_area_templates(self):
        area_template_path = os.path.join(self.data_directory, 'areas')
        for filename in os.listdir(area_template_path):
            if filename.endswith('.json'):
                area_id = filename[:-5]  # Remove '.json' from the filename
                with open(os.path.join(area_template_path, filename), 'r') as f:
                    area_data = json.load(f)
                    self.area_templates[area_id] = AreaTemplate.from_json(area_data)

    def load_room_templates(self):
        room_template_path = os.path.join(self.data_directory, 'rooms')
        for filename in os.listdir(room_template_path):
            if filename.endswith('.json'):
                with open(os.path.join(room_template_path, filename), 'r') as f:
                    room_data = json.load(f)
                    for template in room_data['room_templates']:
                        room_template = RoomTemplate.from_json(template)
                        self.room_templates[room_template.template_id] = room_template

    def get_area_template(self, area_id: str) -> AreaTemplate:
        return self.area_templates.get(area_id)

    def get_room_template(self, template_id: str) -> RoomTemplate:
        return self.room_templates.get(template_id)

    def get_all_area_templates(self) -> Dict[str, AreaTemplate]:
        return self.area_templates

    def get_all_room_templates(self) -> Dict[str, RoomTemplate]:
        return self.room_templates

    def reload_area_template(self, area_id: str):
        area_file_path = os.path.join(self.data_directory, 'areas', f'{area_id}.json')
        if os.path.exists(area_file_path):
            with open(area_file_path, 'r') as f:
                area_data = json.load(f)
                self.area_templates[area_id] = AreaTemplate.from_json(area_data)
        else:
            raise FileNotFoundError(f"Area template file not found for area_id: {area_id}")

    def reload_room_template(self, template_id: str):
        for filename in os.listdir(os.path.join(self.data_directory, 'rooms')):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_directory, 'rooms', filename)
                with open(file_path, 'r') as f:
                    room_data = json.load(f)
                    for template in room_data['room_templates']:
                        if template['template_id'] == template_id:
                            self.room_templates[template_id] = RoomTemplate.from_json(template)
                            return
        raise ValueError(f"Room template not found for template_id: {template_id}")

    def save_area_template(self, area_template: AreaTemplate):
        area_file_path = os.path.join(self.data_directory, 'areas', f'{area_template.area_id}.json')
        with open(area_file_path, 'w') as f:
            json.dump(area_template.to_dict(), f, indent=2)
        self.area_templates[area_template.area_id] = area_template

    def save_room_template(self, room_template: RoomTemplate):
        # For simplicity, we'll save each room template in its own file
        room_file_path = os.path.join(self.data_directory, 'rooms', f'{room_template.template_id}.json')
        with open(room_file_path, 'w') as f:
            json.dump({'room_templates': [room_template.to_dict()]}, f, indent=2)
        self.room_templates[room_template.template_id] = room_template