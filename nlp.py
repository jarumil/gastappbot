import requests
import pandas as pd
import datetime as dt
import json
import typer   

def generate_response(prompt, question, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "max_tokens": 500,
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": question}],
        "stream": True  # Activar streaming
    }
    
    response = requests.post(url, json=data, headers=headers, stream=True)
    
    for line in response.iter_lines():
        if line:
            yield line.decode("utf-8")

response = generate_response(prompt, question, api_key)

for res in response:
    if 'data:' in res:
        res = res.replace('data:', '', 1)
        try:
            res = json.loads(res)
        except json.JSONDecodeError:
            pass
    try:
        print(res["choices"][0]["delta"]["content"], end="")
    except KeyError:
        pass
    except AttributeError:
        pass
    except TypeError:
        pass

if __name__ == "__main__":
    prompt = f'Utilice los artículos proporcionados delimitados por comillas triples para responder preguntas de manera concisa y directa, sin explicaciones largas. Si no se puede encontrar la respuesta en los artículos, escriba "No pude encontrar una respuesta". """{data_str}""". '
    question = 'Pregunta: ¿Como han ido progresando los gastos de tipo propios en 2024?'
    typer.run(generate_response)