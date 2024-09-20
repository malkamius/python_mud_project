import sys
import os
import importlib.util
from typing import List, Callable, TypeVar, Protocol
from enum import IntEnum, auto
from .character.character import Character, CharacterPositions

# Define the CommandFunction protocol
class CommandFunction(Protocol):
    def __call__(self, character: Character, arguments: str) -> None:
        ...

# Use CommandFunction as our callable type
CommandCallable = CommandFunction



class CommandTypeEnum(IntEnum):
    Movement = auto()
    Position = auto()
    Information = auto()
    ItemManipulation = auto()
    Combat = auto()
    Skill = auto()
    Immortal = auto()

class CommandInformation:
    def __init__(self, name: str, minimum_position: CharacterPositions, minimum_level: int, 
                 skill_name: str, func: CommandCallable, command_type: CommandTypeEnum, zorder: int):
        self.name = name
        self.minimum_position = minimum_position
        self.minimum_level = minimum_level
        self.skill_name = skill_name
        self.func = func
        self.command_type = command_type
        self.zorder = zorder

# List to store CommandInformation objects
commands: List[CommandInformation] = []

class CommandAttribute:
    """Attribute class for marking functions as commands."""
    def __init__(self, name: str = None, minimum_position: CharacterPositions = CharacterPositions.Dead, 
                 minimum_level: int = 0, skill_name: str = "", command_type: CommandTypeEnum = CommandTypeEnum.Information,
                 zorder: int = 0):
        self.name = name
        self.minimum_position = minimum_position
        self.minimum_level = minimum_level
        self.skill_name = skill_name
        self.command_type = command_type
        self.zorder = zorder

    def __call__(self, func: CommandCallable):
        command_name = self.name or func.__name__
        command_info = CommandInformation(command_name, self.minimum_position, self.minimum_level, 
                                          self.skill_name, func, self.command_type, self.zorder)
        commands.append(command_info)
        return func

def load_module(file_path: str):
    module_name = file_path[len(os.getcwd()) + 1:].replace(os.path.sep, ".").rstrip(".py")# os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    
    # Add the module's directory to sys.path temporarily
    module_dir = os.path.dirname(file_path)
    sys.path.insert(0, module_dir)
    
    try:
        spec.loader.exec_module(module)
    finally:
        # Remove the module's directory from sys.path
        sys.path.pop(0)

def load_commands_from_folder(folder_path: str):
    abs_folder_path = os.path.abspath(folder_path)
    
    # Add the parent directory of the commands folder to sys.path
    parent_dir = os.path.dirname(abs_folder_path)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    for root, _, files in os.walk(abs_folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                load_module(file_path)
    
    # Sort the commands
    sort_commands()

    # Print all loaded commands
    for command in commands:
        print(f"Loaded command: {command.name}")
        print(f"  Command Type: {command.command_type.name}")
        print(f"  ZOrder: {command.zorder}")
        print(f"  Minimum Position: {command.minimum_position.name}")
        print(f"  Minimum Level: {command.minimum_level}")
        print(f"  Skill Name: {command.skill_name}")
        print(f"  Function: {command.func.__name__}")
        print()

def sort_commands():
    """Sort the commands list by command_type, zorder, and then alphabetically by name."""
    global commands
    commands.sort(key=lambda cmd: (cmd.command_type.value, cmd.zorder, cmd.name))
