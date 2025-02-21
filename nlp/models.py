from abc import ABC, abstractmethod
import os
import json
import constants.constants as cts
import requests


class Model(ABC):
    def __init__(self, name: str):
        self._model = name

    @abstractmethod
    def request(self, prompt: str, question: str) -> requests.Response:
        pass

    @abstractmethod
    def process_stream_request(self, request: requests.Response):
        pass


class OpenRouterModel(Model):
    def __init__(self, name: str, max_tokens: int = 1000, stream: bool = True):
        super().__init__(name)
        self._max_tokens = max_tokens
        self._stream = stream
        self._url = "https://openrouter.ai/api/v1/chat/completions"

        with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE), 'r') as file:
            api_credentials = json.load(file)
        
        self._headers = {"Authorization": f"Bearer {api_credentials['openrouter_key']}"}

    def request(self, prompt: str, question: str) -> requests.Response:
        data = {
            "max_tokens": self._max_tokens,
            "model": self._model,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": question}],
            "stream": self._stream,
        }

        return requests.post(self._url, json=data, headers=self._headers, stream=self._stream)
    
    def process_stream_request(self, response: requests.Response):
        for line in response.iter_lines():
            if line:
                res = line.decode("utf-8")
                if 'data:' in res:
                    res = res.replace('data:', '', 1)
                    if 'error' in res:
                        print(f"error: {res}")
                        return
                    else:
                        try:
                            res = json.loads(res)
                            yield res["choices"][0]["delta"]["content"]
                        except:
                            continue
        else:
            print(self._model)
            return
