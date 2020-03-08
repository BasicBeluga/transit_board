from pathlib import Path
import os
import json

home = str(Path.home())
DEFAULT_SETTINGS_PATH = home + "/" + "transit_board_settings.json"

class Settings():
    def __init__(self, path=DEFAULT_SETTINGS_PATH):
        self.settings = None
        
        if not os.path.isfile(path):
            with open(path, 'w') as json_file:
                json_file.write('{}')
        
        with open(path, 'r') as json_file:
            contents = json.loads(json_file.read())
            self.settings = contents
