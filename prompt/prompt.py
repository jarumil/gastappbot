from prompt.data import Data
import json
from utils import get_class_from_string

with open("config.json", "r") as f:
    config = json.load(f)

DataClass: Data = get_class_from_string(config["data"])

class Prompt:
    """
    Class to generate the prompt
    """
    def __init__(self):
        self._data = DataClass()
        with open("config.json", "r") as f:
            config = json.load(f)
        self._prompt = config["prompt"]

    @property
    def prompt(self) -> str:
        return self.generate_prompt()

    def generate_prompt(self) -> None:
        return self._prompt.format(data_str=self._data.filtered_data().to_csv(index=False))
