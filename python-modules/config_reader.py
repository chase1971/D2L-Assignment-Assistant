"""
Config Reader for D2L Assignment Extractor
Reads configuration from Electron app's config file
"""
import json
import os
import sys

def get_config_path():
    """Get the path to the config file"""
    # In Electron, config is stored in app.getPath('userData')
    # On Windows, this is typically: %APPDATA%\D2L Assignment Extractor\config.json
    
    # Try multiple possible locations
    possible_paths = [
        # Windows AppData
        os.path.join(os.getenv('APPDATA', ''), 'D2L Assignment Extractor', 'config.json'),
        # Fallback: user's home directory
        os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'D2L Assignment Extractor', 'config.json'),
        # Development/testing: current directory
        os.path.join(os.path.dirname(__file__), 'config.json')
    ]
    
    for config_path in possible_paths:
        if os.path.exists(config_path):
            return config_path
    
    return None

def load_config():
    """Load configuration from file"""
    config_path = get_config_path()
    
    if not config_path or not os.path.exists(config_path):
        # Return defaults if config doesn't exist
        return {
            'downloadsPath': os.path.join(os.path.expanduser('~'), 'Downloads'),
            'rostersPath': os.path.join(os.path.expanduser('~'), 'My Drive', 'Rosters etc'),
            'drive': 'C',
            'firstRun': True
        }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        print(f"Warning: Could not load config file: {e}", file=sys.stderr)
        # Return defaults on error
        return {
            'downloadsPath': os.path.join(os.path.expanduser('~'), 'Downloads'),
            'rostersPath': os.path.join(os.path.expanduser('~'), 'My Drive', 'Rosters etc'),
            'drive': 'C',
            'firstRun': True
        }

def get_downloads_path():
    """Get the configured downloads path"""
    config = load_config()
    downloads_path = config.get('downloadsPath', '')
    
    if downloads_path and os.path.exists(downloads_path):
        return downloads_path
    
    # Fallback to default
    default_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    return default_path

def get_rosters_path():
    """Get the configured rosters path, checking both G and C drives"""
    config = load_config()
    rosters_path = config.get('rostersPath', '')
    
    if rosters_path and os.path.exists(rosters_path):
        return rosters_path
    
    # Fallback: Try both G:\ and C:\ drives (prioritize G, then C)
    username = os.getenv('USERNAME', 'chase')
    drives_to_try = ['G', 'C']
    
    for drive_letter in drives_to_try:
        # Try two path patterns:
        # 1. Direct drive root (for mapped drives like G: Google Drive)
        #    G:\My Drive\Rosters etc
        # 2. User profile path (for local drives like C:)
        #    C:\Users\chase\My Drive\Rosters etc
        
        path_patterns = [
            os.path.join(f"{drive_letter}:\\", "My Drive", "Rosters etc"),
            os.path.join(f"{drive_letter}:\\", "Users", username, "My Drive", "Rosters etc")
        ]
        
        for test_path in path_patterns:
            if os.path.exists(test_path):
                return test_path
    
    # Ultimate fallback if nothing exists
    drive = config.get('drive', 'C')
    default_path = os.path.join(f"{drive}:\\", "Users", username, "My Drive", "Rosters etc")
    return default_path

def get_drive():
    """Get the configured drive letter"""
    config = load_config()
    return config.get('drive', 'C')

