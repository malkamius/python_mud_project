from typing import Dict, Tuple, List, Optional
from .room_instance import RoomInstance
from .room_template import RoomTemplate
from .area_template import AreaTemplate

class AreaInstance:
    def __init__(self, template : AreaTemplate, name: Optional[str] = None):
        self.template_id: str = template.name
        self.name: str = name or f"Instance of {self.template_id}"
        self.rooms: Dict[str, RoomInstance] = {}
        self.generation_complete: bool = False
        self.entry_point: Optional[Tuple[int, int, int]] = None
        self.template : AreaTemplate = template

    def generate_room(self, room_type: str, coordinates: Tuple[int, int, int]) -> RoomInstance:
        template = RoomTemplate.get_template(room_type)
        new_room = RoomInstance(template, self, coordinates)
        self.rooms[coordinates] = new_room
        
        if not self.entry_point:
            self.entry_point = coordinates
        
        return new_room

    def get_room(self, id : str) -> Optional[RoomInstance]:
        return self.rooms.get(id) or self.rooms.get(f"0_{id}")

    def add_room(self, room: RoomInstance) -> None:
        self.rooms[room.id] = room

    def remove_room(self, coordinates: Tuple[int, int, int]) -> None:
        if coordinates in self.rooms:
            del self.rooms[coordinates]

    def get_adjacent_coordinates(self, coordinates: Tuple[int, int, int]) -> Dict[str, Tuple[int, int, int]]:
        x, y, z = coordinates
        return {
            'north': (x, y + 1, z),
            'south': (x, y - 1, z),
            'east': (x + 1, y, z),
            'west': (x - 1, y, z),
            'up': (x, y, z + 1),
            'down': (x, y, z - 1)
        }

    def generate_adjacent_rooms(self, coordinates: Tuple[int, int, int]) -> None:
        current_room = self.get_room(coordinates)
        if not current_room:
            return

        adjacent_coords = self.get_adjacent_coordinates(coordinates)
        for direction, exit_type in current_room.exits.items():
            if exit_type and adjacent_coords[direction] not in self.rooms:
                self.generate_room(exit_type, adjacent_coords[direction])

    def complete_generation(self) -> None:
        self.generation_complete = True

    def get_all_rooms(self) -> List[RoomInstance]:
        return list(self.rooms.values())

    def get_area_bounds(self) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        if not self.rooms:
            return ((0, 0, 0), (0, 0, 0))
        
        all_coords = list(self.rooms.keys())
        min_x = min(coord[0] for coord in all_coords)
        max_x = max(coord[0] for coord in all_coords)
        min_y = min(coord[1] for coord in all_coords)
        max_y = max(coord[1] for coord in all_coords)
        min_z = min(coord[2] for coord in all_coords)
        max_z = max(coord[2] for coord in all_coords)
        
        return ((min_x, min_y, min_z), (max_x, max_y, max_z))

    def to_dict(self) -> Dict:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'rooms': {str(coord): room.to_dict() for coord, room in self.rooms.items()},
            'generation_complete': self.generation_complete,
            'entry_point': self.entry_point
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AreaInstance':
        area = cls(data['template_id'], data['name'])
        area.generation_complete = data['generation_complete']
        area.entry_point = tuple(data['entry_point']) if data['entry_point'] else None
        for coord_str, room_data in data['rooms'].items():
            coord = tuple(map(int, coord_str.strip('()').split(',')))
            room = RoomInstance.from_dict(room_data, area, coord)
            area.rooms[coord] = room
        return area