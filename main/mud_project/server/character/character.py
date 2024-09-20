
from ..world.room_template import RoomTemplate
from enum import IntEnum, auto

class CharacterPositions(IntEnum):
    Dead = 0
    Mortal = 1
    Incapacitated = 2
    Stunned = 3
    Sleeping = 4
    Resting = 5
    Sitting = 6
    Fighting = 7
    Standing = 8

class Character:
    name : str = ""
    short_description : str = ""
    long_description : str = ""
    room : RoomTemplate = None
    
    def send(self, data):
        pass

    def CharacterFromRoom(self):
        if self.room != None and self in self.room.characters:
            self.room.characters.remove(self)
            self.room = None
    
    def CharacterToRoom(self, room : RoomTemplate):
        # double check that we are not already in a room
        # otherwise, silently remove and move to next room
        self.CharacterFromRoom() 
        room.characters.insert(0, self)
        self.room = room

        