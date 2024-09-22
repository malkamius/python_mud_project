from datetime import datetime, timedelta
from .reset_data import ResetTypes
from ..character.npc_character import NPCCharacter
from logging import getLogger

class ResetManager:

    def __init__(self, world_manager):
        from .world_manager import WorldManager
        self.world_manager : WorldManager = world_manager
        self.logger = getLogger(__name__)
    
    def ResetAreas(self):
        time = datetime.now()
        for area in self.world_manager.area_templates.values():
            if area.last_reset != None:
                delta = time - area.last_reset

            if area.last_reset == None or delta.total_seconds() / 60 >= 5:
                area.last_reset = time
                for reset in area.resets:
                    if reset.resetType == ResetTypes.NPC:
                        room = self.world_manager.room_templates[reset.roomVnum] if reset.roomVnum in self.world_manager.room_templates else None
                        if room == None:
                            self.logger.warning(f"Failed to locate room template for reset in area {reset.area.name}: {reset.roomVnum}")
                            continue
                        inRoomCount = 0
                        for other in room.characters:
                            if isinstance(other, NPCCharacter) and other.id == reset.spawnVnum:
                                inRoomCount += 1
                        npc_template = None
                        if reset.spawnVnum in self.world_manager.npc_templates:
                            npc_template = self.world_manager.npc_templates[reset.spawnVnum]
                        if npc_template == None:
                            self.logger.warning(f"Failed to locate npc template for reset in area {reset.area.name}: {reset.spawnVnum}")
                            continue

                        if npc_template.instance_count < reset.maxCount and inRoomCount < reset.count:
                            npc = NPCCharacter()
                            npc.name = npc_template.name
                            npc.long_description = npc_template.long_description
                            npc.short_description = npc_template.short_description
                            npc.CharacterToRoom(room)
                            npc_template.instance_count += 1
