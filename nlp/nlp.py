from prompt.prompt import Prompt
from nlp.models import OpenRouterModel
import json

class NLP:
    def __init__(self):
        self._prompt = Prompt()

        with open("config.json", "r") as f:
            config = json.load(f)
        self._question = config["question"]
        openrouter_models = config["openrouter_models"]

        self._models = [
            OpenRouterModel(**params) for params in openrouter_models
        ]

    def generate_response(self, question: str):
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
