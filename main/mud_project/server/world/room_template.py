from typing import Dict, List, Any
import random
from enum import Enum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..character.character import Character

class DirectionEnum(Enum):
    North = 0
    East = 1
    South = 2
    West = 3
    Up = 4
    Down = 5

class ReverseDirectionEnum(Enum):
    North = DirectionEnum.South
    East = DirectionEnum.West
    South = DirectionEnum.North
    West = DirectionEnum.East
    Up = DirectionEnum.Down
    Down = DirectionEnum.Up

class RoomTemplate:


    def __init__(self, template_data: Dict[str, Any] = None):
        from ..character.character import Character
        self.characters : List[Character] = []
        self.exits : List[ExitData] = []

        #self.send = send
        if template_data != None:
            
            #self.items : List[ItemInstance] = []
            self.template_id: int = template_data['template_id']
            self.name: str = template_data['name']
            self.description: str = template_data['description']
            self.exits: Dict[DirectionEnum, ExitData] = template_data.get('exits', {})
            self.features: List[str] = template_data.get('features', [])
            self.npc_chances: List[Dict[str, Any]] = template_data.get('npc_chances', [])
            self.item_chances: List[Dict[str, Any]] = template_data.get('item_chances', [])
            self.flags: List[str] = template_data.get('flags', [])

    def send(self, text: str, ignore: List['Character'] = None):
        for target in self.characters:
            if ignore == None or not target in ignore:
                target.send(text)

    def GetExit(self, direction: DirectionEnum) -> 'ExitData': 
        if not direction in self.exits:
            return None
        else:
            return self.exits[direction]
        
    

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'RoomTemplate':
        return cls(json_data)

    def get_possible_exits(self) -> Dict[str, str]:
        return {direction: exit_data['type'] for direction, exit_data in self.exits.items()}

    def roll_exits(self) -> Dict[str, str]:
        return {
            direction: exit_data['type']
            for direction, exit_data in self.exits.items()
            if random.random() < exit_data['chance']
        }

    def roll_npcs(self) -> List[str]:
        return [
            npc['type']
            for npc in self.npc_chances
            for _ in range(random.randint(0, npc['max']))
            if random.random() < npc['chance']
        ]

    def roll_items(self) -> List[str]:
        return [
            item['type']
            for item in self.item_chances
            for _ in range(random.randint(0, item['max']))
            if random.random() < item['chance']
        ]

    def has_flag(self, flag: str) -> bool:
        return flag in self.flags

    def to_dict(self) -> Dict[str, Any]:
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'exits': self.exits,
            'features': self.features,
            'npc_chances': self.npc_chances,
            'item_chances': self.item_chances,
            'flags': self.flags
        }

    @staticmethod
    def get_template(template_id: str) -> 'RoomTemplate':
        # This method would typically load the template from a database or file
        # For now, we'll just return a dummy template
        dummy_data = {
            'template_id': template_id,
            'name': f'Room {template_id}',
            'description': 'A nondescript room.',
            'exits': {'north': {'type': 'default_room', 'chance': 1.0}},
            'features': ['wall', 'floor'],
            'npc_chances': [{'type': 'generic_npc', 'chance': 0.5, 'max': 1}],
            'item_chances': [{'type': 'generic_item', 'chance': 0.3, 'max': 2}],
            'flags': ['indoors']
        }
        return RoomTemplate(dummy_data)
    
class ExitData:
    Direction : DirectionEnum
    Destination: RoomTemplate = field(default=None,metadata=config(exclude=True))
    DestinationVnum : int
