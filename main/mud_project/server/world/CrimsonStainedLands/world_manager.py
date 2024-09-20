from typing import Dict, Tuple, Optional
import json
import os
import time
from ..room_template import RoomTemplate
from .area_template import CSLAreaTemplate
from ..world_manager import WorldManager
import asyncio

class CrimsonStainedLandsWorldManager(WorldManager):
    def __init__(self, configWorld, db_handler):
        super().__init__(configWorld, db_handler)

    async def add_template(self, obj):
        await asyncio.sleep(0)
        if isinstance(obj, RoomTemplate):
            self.room_templates[obj.template_id] = obj

    async def load_templates(self):
        # Load area templates
        areas_path = '../../../CSLData/areas'
        for filename in os.listdir(areas_path):
            if filename.endswith('_Programs.xml') == False and filename.endswith('.xml'):
                area_path = os.path.join(areas_path, filename)
                area = CSLAreaTemplate(self, area_path)
                await area.load()
                self.area_templates[area.name] = area
                self.logger.info(f"Loaded {area.name}")

    def get_room_template(self, template_id: str) -> Optional[RoomTemplate]:
        return self.room_templates.get(template_id)

    def get_area_template(self, template_id: str) -> Optional[Dict]:
        return self.area_templates.get(template_id)