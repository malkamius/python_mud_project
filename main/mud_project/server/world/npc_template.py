from typing import Dict, List, Any

class NPCTemplate:
    def __init__(self, template_data: Dict[str, Any] = None):
        self.id : int = 0
        self.name : str = ""
        self.short_description : str = ""
        self.long_description : str = ""
        self.description : str = ""
        self.instance_count : int = 0