from prompt.prompt import Prompt
from nlp.models import OpenRouterModel
from utils import get_class_from_string
import json

class NLP:
    """
    Natural Language Processing class for generating responses using multiple models.
    """

    def __init__(self):
        """
        Initialize the NLP class with configuration from a JSON file.
        """
        with open("config.json", "r") as f:
            config = json.load(f)

        self._prompt: Prompt = get_class_from_string(config["prompt"])()
        self._question: str = config["question"]
        openrouter_models: list = config["openrouter_models"]

        self._models = [
            OpenRouterModel(**params) for params in openrouter_models
        ]

    def generate_response(self, question: str):
        """
        Generate a response to a given question using the configured models.

        Parameters
        ----------
        question : str
            The question to generate a response for.

        Yields
        ------
        str
            The generated response from the models.
        """
        question = self._question.format(question=question)

        for model in self._models:
            response = model.request(self._prompt.prompt, question)

            any_valid_response = False

            for msg in model.process_stream_request(response):
                if msg:
                    any_valid_response = True
                yield msg
            if any_valid_response:
                return
        msg = "No response from any model"
        print(msg)
        return msg
