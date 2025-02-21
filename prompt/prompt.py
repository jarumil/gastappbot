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
        prompt = self._prompt

        data = self._data.filtered_data()
        for (year, month), sub_df in data.groupby(["Año", "Mes"]):
            prompt += f'Aqui tienes los datos de {month} del {year}:\n"""{sub_df.drop(columns=["Año", "Mes"]).to_csv(index=False)}"""\n\n'

        return prompt
