from ...character.character import Character, CharacterPositions
from ...world.room_template import DirectionEnum, ReverseDirectionEnum
from ..information.look import look
from ...commands import CommandAttribute, CommandTypeEnum

def move_char(character : Character, direction : DirectionEnum):
    exitdata = character.room.GetExit(direction)
    if exitdata == None or \
    exitdata == None or \
    exitdata.Destination == None:
        character.send("Alas, you can't go that way.\r\n")
    else:
        #for other in character.room.characters
        for other in character.room.characters:
            if other != character:
                other.send(f"{character.name} leaves {direction.name.lower()}.\r\n")
        character.CharacterFromRoom()
        character.CharacterToRoom(exitdata.Destination)
        for other in character.room.characters:
            if other != character:
                other.send(f"{character.name} arrives from the {ReverseDirectionEnum[direction.name].value.name.lower()}.\r\n")
        look(character, "")

@CommandAttribute(name="north", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Movement, zorder=10)
def east(character : Character, arguments : str):
    move_char(character, DirectionEnum.North)
    
@CommandAttribute(name="east", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Movement, zorder=10)
def east(character : Character, arguments : str):
    move_char(character, DirectionEnum.East)

@CommandAttribute(name="south", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Movement, zorder=10)
def east(character : Character, arguments : str):
    move_char(character, DirectionEnum.South)

@CommandAttribute(name="west", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Movement, zorder=10)
def east(character : Character, arguments : str):
    move_char(character, DirectionEnum.West)

@CommandAttribute(name="up", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Movement, zorder=10)
def east(character : Character, arguments : str):
    move_char(character, DirectionEnum.Up)

@CommandAttribute(name="down", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Movement, zorder=10)
def east(character : Character, arguments : str):
    move_char(character, DirectionEnum.Down)