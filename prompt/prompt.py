from prompt.data import Data, MyData
from abc import ABC, abstractmethod
import json

class Prompt(ABC):
    """
    Abstract class to generate the prompt.

    Attributes
    ----------
    _data : Data
        Data object.
    _prompt : str
        Prompt template.
    """
    def __init__(self, data: Data):
        """
        Initializes the Prompt object.
        
        Parameters
        ----------
        data : Data
            Data object.
        """
        self._data = data
        with open("config.json", "r") as f:
            config = json.load(f)
        self._prompt = config["prompt"]

    @property
    def prompt(self) -> str:
        """
        Returns
        -------
        str
            The generated prompt.
        """
        return self.generate_prompt()

    @abstractmethod
    def generate_prompt(self) -> str:
        """
        Abstract method to generate the prompt.

        Returns
        -------
        str
            The generated prompt.
        """
        pass
    

class MyPrompt(Prompt):
    """
    Class to generate my prompt.
    """
    def __init__(self):
        super().__init__(MyData())

    def generate_prompt(self) -> str:
        """
        Generates the prompt grouping the data by year and month.

        Returns
        -------
        str
            The generated prompt.
        """
        prompt = self._prompt

        for (year, month), sub_df in self._data.filtered_data.groupby(["Año", "Mes"], sort=False):
            prompt += f'Aqui tienes los datos de {month} del {year}:\n"""{sub_df.drop(columns=["Año", "Mes"]).to_csv(index=False)}"""\n\n'

        return prompt
