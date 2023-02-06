#standard library
import os
import json

#third party
from pathlib import Path

#module
#sub-module


class Config_creator():
    def __init__(self, page):
        """create file config, pass if exist
        """            
        self.config_dir_path = Path(os.path.join(os.getcwd(), r'config'))
        # will create directory, if it exists will do nothing
        self.config_dir_path.mkdir(parents=True, exist_ok=True)
        self.config_path = Path(os.path.join(self.config_dir_path, 'config.json'))
        # will create file, if it exists will do nothing
        self.config_path.touch(exist_ok=True)
        self.config = self.get_config()
        self.check_or_create_page(page)

    def __call__(self):
        return self.get_config()

    def get_path(self):
        return self.config_path

    def get_dir_path(self):
        return self.config_dir_path
    
    def add_config(self, page, key, value):
        self.check_or_create_page(page)
        self.config[page][key] = value
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def check_or_create_page(self, page):
        """check page in config, or it would create a new one
        """  
        if page not in self.config:
            self.config[page] = {}
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

    def get_config(self):
        config = None
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except:
            with open(self.config_path, 'w') as f:
                f.write('{}')
            return {}
    
    
if __name__ == '__main__':
    aa = Config_creator()
    aa.add_config('FW', 'path', 123)