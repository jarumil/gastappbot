from abc import ABC, abstractmethod
import os
import json
import constants.constants as cts
import requests


class Model(ABC):
    """
    Abstract class to define a language model interface
    
    Attributes
    ----------
    _model : str
        Model name
    """

    def __init__(self, name: str):
        """
        Initializes the model with the given name
        
        Parameters
        ----------
        name : str
            Model name
        """
        self._model = name

    @abstractmethod
    def request(self, prompt: str, question: str) -> requests.Response:
        """
        Abstract method to make a request to the model
        
        Parameters
        ----------
        prompt : str
            Prompt to send to the model
        question : str
            Question to send to the model
        
        Returns
        -------
        requests.Response
            Response from the model
        """
        pass

    @abstractmethod
    def process_stream_request(self, request: requests.Response):
        """
        Abstract method to process the stream request
        
        Parameters
        ----------
        request : requests.Response
            Response from the model
        
        Returns
        -------
        generator
            Generator to process the stream request
        """
        pass


class OpenRouterModel(Model):
    """
    OpenRouter model implementation for handling requests
    
    Attributes
    ----------
    _model : str
        Model name
    _max_tokens : int
        Maximum num of tokens for the response
    _stream : bool
        Whether to stream the response
    _url : str
        OpenRouter API URL
    _headers : dict
        Headers containing the API key
    """

    def __init__(self, name: str, max_tokens: int = 1000, stream: bool = True):
        """
        Initializes the OpenRouter model with the given parameters
        
        Parameters
        ----------
        name : str
            Model name
        max_tokens : int
            Maximum num of tokens for the response
        stream : bool
            Whether to stream the response
        """
        super().__init__(name)
        self._max_tokens = max_tokens
        self._stream = stream
        self._url = "https://openrouter.ai/api/v1/chat/completions"

        with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE), 'r') as file:
            api_credentials = json.load(file)
        
        self._headers = {"Authorization": f"Bearer {api_credentials['openrouter_key']}"}

    def request(self, prompt: str, question: str) -> requests.Response:
        """
        Makes a request to the OpenRouter model
        
        Parameters
        ----------
        prompt : str
            The system prompt to provide context for the model
        question : str
            The user question to ask the model
        
        Returns
        -------
        requests.Response
            The API response
        """
        data = {
            "max_tokens": self._max_tokens,
            "model": self._model,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": question}],
            "stream": self._stream,
        }

        return requests.post(self._url, json=data, headers=self._headers, stream=self._stream)
    
    def process_stream_request(self, response: requests.Response):
        """
        Processes the stream response from OpenRouter.

        Parameters
        ----------
        response : requests.Response
            The response from the model
        
        Yields
        ------
        str
            The generated response from the model
        
        Notes
        -----
        - Skips malformed responses
        """
        for line in response.iter_lines():
            if line:
                res = line.decode("utf-8")
                if 'data:' in res:
                    res = res.replace('data:', '', 1)
                    try:
                        res = json.loads(res)
                    except:
                        continue
                    if 'error' in res.keys():
                        print(f"error: {res['error']['message']}")
                        return
                    else:
                        yield res["choices"][0]["delta"]["content"]
        else:
            print(self._model)
            return
