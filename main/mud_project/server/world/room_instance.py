import copy
from .room_template import RoomTemplate
class RoomInstance:
    def __init__(self, template : RoomTemplate, area):
        self.id = ""
        self.template = template
        self.area = area
        self.name = template.name
        self.description = template.description
        self.exits = copy.deepcopy(template.exits)
        self.npcs = []
        self.items = []
        self.generate_content()

    def generate_content(self):
        # Generate exits, NPCs, and items based on template chances
        pass