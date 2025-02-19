import requests
import json
import typer
from prompt import Prompt
import constants.constants as cts
import os

app = typer.Typer()

@app.command()
def generate_response(question: str):
    question = cts.QUESTION.format(question=question)
    prompt = Prompt()

    with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE), 'r') as file:
        api_credentials = json.load(file)

    api_key = api_credentials["openrouter_key"]

    models = ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat:free"]

    for model in models:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "max_tokens": 1000,
            "model": model,
            "messages": [{"role": "system", "content": prompt.prompt}, {"role": "user", "content": question}],
            "stream": True  # Activar streaming
        }
        
        response = requests.post(url, json=data, headers=headers, stream=True)
        
        for line in response.iter_lines():
            if line:
                # yield line.decode("utf-8")
                res = line.decode("utf-8")
                if 'data:' in res:
                    res = res.replace('data:', '', 1)
                    if 'error' in res:
                        break
                    else:
                        try:
                            res = json.loads(res)
                            msg = res["choices"][0]["delta"]["content"]
                            yield msg
                        except:
                            continue
        else:
            print(model)
            return
    yield res
        

if __name__ == "__main__":
    app()
    # for rr in generate_response("¿Cuanto he gastado en luz en febrero de 2023?"):
    #     print(rr, end="")

