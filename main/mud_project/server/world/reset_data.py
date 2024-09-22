from enum import IntEnum, auto
class ResetTypes(IntEnum):
    NPC = auto()
    Equip = auto()
    Give = auto()
    Item = auto()
    Put = auto()
    EquipRandom = auto()



class ResetData:
    _lastNPCVnum : int = 0
    _lastItemVnum : int = 0

    def __init__(self):
        from .area_template import AreaTemplate
        self.area : AreaTemplate = None
        self.resetType : ResetTypes = ResetTypes.NPC
        self.spawnVnum : int = 0
        self.spawnVnums : str = ""
        self.roomVnum : int = 0
        self.count : int = 0
        self.maxCount : int = 0


