import yaml
import os
from typing import Dict, Any

DEFAULT_CONFIG = {
    'server': {
        'host': 'localhost',
        'port': 3000,
        'ssl_port': 3001,
        'websocket_port': 3002,
        'max_connections': 100
    },
    'database': {
        'type': 'sqlite',
        'path': 'mud_database.sqlite'
    },
    'world': {
        'data_directory': 'data/world',
        'start_area': 'limbo'
    },
    'game': {
        'tick_rate': 60,  # Game loop ticks per second
        'max_players': 50
    },
    'logging': {
        'level': 'INFO',
        'file': 'mud_server.log'
    },
    'protocols': {
        'telnet': True,
        'ssl': True,
        'websocket': True,
        'ssl-cert': "localhost_cert.pem",
        'ssl-key': 'localhost_key.pem'
    }
}

def load_config(config_file: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load the configuration from a YAML file and merge it with the default config.
    
    Args:
        config_file (str): Path to the configuration file.
    
    Returns:
        Dict[str, Any]: The merged configuration dictionary.
    """
    config = DEFAULT_CONFIG.copy()

    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            file_config = yaml.safe_load(f)
        
        # Recursively update the default config with values from the file
        deep_update(config, file_config)
    else:
        print(f"Warning: Config file '{config_file}' not found. Using default configuration.")
    
    return config

def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """
    Recursively update a nested dictionary with another dictionary.
    
    Args:
        base_dict (Dict[str, Any]): The dictionary to update.
        update_dict (Dict[str, Any]): The dictionary with update values.
    """
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            deep_update(base_dict[key], value)
        else:
            base_dict[key] = value

def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a value from the config using a dot-separated key path.
    
    Args:
        config (Dict[str, Any]): The configuration dictionary.
        key_path (str): Dot-separated path to the desired config value.
        default (Any): Default value to return if the key is not found.
    
    Returns:
        Any: The config value, or the default if not found.
    """
    keys = key_path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value

# Example usage
if __name__ == "__main__":
    config = load_config()
    print("Server host:", get_config_value(config, 'server.host'))
    print("Database path:", get_config_value(config, 'database.path'))
    print("Non-existent value:", get_config_value(config, 'non.existent.key', 'default_value'))