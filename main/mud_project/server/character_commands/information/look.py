from ...character.character import Character, CharacterPositions
from ...commands import CommandAttribute, CommandTypeEnum

@CommandAttribute(name="look", minimum_position=CharacterPositions.Standing, minimum_level=1, 
                  skill_name=None, command_type=CommandTypeEnum.Information, zorder=10)
def look(character : Character, arguments : str):
    if character == None:
        pass
    elif character.room == None:
        character.send("You aren't in a room.\r\n")
    else:
        character.send(f"  {character.room.name}\r\n")
        character.send(f"{character.room.description}\r\n")
        exitsstr = ""
        for direction, exitdata in character.room.exits.items():
            if exitdata.Destination != None:
                if len(exitsstr) != 0:
                    exitsstr += " "
                exitsstr += direction.name.lower()
        if len(exitsstr) == 0:
            exitsstr = "none"
        character.send(f"\r\n[Exits: {exitsstr}]\r\n")

        for other in character.room.characters:
            if other != character:
                character.send(f"{other.name} stands here.\r\n")
                