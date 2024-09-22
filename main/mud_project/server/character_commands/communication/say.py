from ...character.character import Character, CharacterPositions
from ...commands import CommandAttribute, CommandTypeEnum
from ...color import colorize

@CommandAttribute(name="say", minimum_position=CharacterPositions.Resting, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Information, zorder=10)
def say(character : Character, arguments : str):
    if character.room == None:
        return;
    arguments = arguments.strip()
    nocolor = colorize(arguments, False, False, False)
    if len(arguments) == 0 or len(nocolor) == 0:
        character.send("Say what?\r\n")
    else:
        character.room.send(f"\\y{character.name} says '{arguments}\\y'\\x\r\n", [character])
        character.send(f"\\yYou say '{arguments}\\y'\\x\r\n")