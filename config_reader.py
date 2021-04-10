import json

class ConfigReader():
    @staticmethod
    def read_config_file(config_file:str) -> dict:
        with open(f"./{config_file}",encoding = "utf-8") as config_file:
            config_file_dict = json.load(config_file)
            return config_file_dict




