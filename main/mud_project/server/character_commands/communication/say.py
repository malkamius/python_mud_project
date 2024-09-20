from ...character.character import Character, CharacterPositions
from ...commands import CommandAttribute, CommandTypeEnum

@CommandAttribute(name="say", minimum_position=CharacterPositions.Resting, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Information, zorder=10)
def say(character : Character, arguments : str):
    if character.room == None:
        return;
    character.room.send(f"{character.name} says '{arguments}'\\x\r\n", [character])
    character.send(f"You say '{arguments}'\\x\r\n")