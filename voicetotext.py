import locale
import pandas as pd
from transformers import Trainer, TrainingArguments, BertTokenizer, BertForQuestionAnswering
from datasets import Dataset

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Cargar los datos desde el archivo CSV
df = pd.read_csv('data.csv')

data = df.drop(columns=["Total", "Dividido"])
data["Fecha"] = pd.to_datetime(data["Fecha"], format='%d/%m/%Y')
data["Parcial"] = data["Parcial"].str.replace(".", "").str.replace(",", ".").astype(float)

# Agrupar por 'Fecha' y 'Concepto' para obtener los gastos mensuales por categoría
df_grouped = data.groupby([data['Fecha'].dt.to_period('M'), 'Concepto']).agg({'Parcial': 'sum'}).reset_index()
df_grouped["Parcial"] = df_grouped["Parcial"].round(2)

# Cargar el tokenizer y modelo
tokenizer = BertTokenizer.from_pretrained("mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es")
model = BertForQuestionAnswering.from_pretrained("mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es")

# Crear una lista de ejemplos de pregunta-respuesta
questions = []
contexts = []
answers = []
start_positions = []
end_positions = []

for _, row in df_grouped.iterrows():
    question = f"¿Cuánto gasté en {row['Concepto']} en {row['Fecha'].strftime('%B')} de {row['Fecha'].year}?"
    context = f"En {row['Fecha'].strftime('%B')} de {row['Fecha'].year}, los gastos fueron: {row['Concepto']} = {row['Parcial']}€."
    answer = str(row["Parcial"])  # Respuesta directa numérica
    
    questions.append(question)
    contexts.append(context)
    answers.append(answer)

    # Tokenizar el contexto y la pregunta
    encodings = tokenizer(question, context, truncation=True, padding="max_length", max_length=512, return_tensors="pt")

    # Buscar la respuesta en el contexto y obtener las posiciones de inicio y fin
    start_pos = context.find(answer)
    end_pos = start_pos + len(answer)

    # Convertir las posiciones de caracteres a posiciones de tokens
    start_token = encodings.char_to_token(start_pos) if start_pos >= 0 else -1
    end_token = encodings.char_to_token(end_pos) if end_pos >= 0 else -1
    
    # Agregar las posiciones al dataset
    start_positions.append(start_token)
    end_positions.append(end_token)

# Convertir las preguntas y respuestas en un formato adecuado para Hugging Face Datasets
train_data = {
    'question': questions, 
    'context': contexts, 
    'answer': answers, 
    'start_position': start_positions,
    'end_position': end_positions
}

train_dataset = Dataset.from_dict(train_data)

# Tokenizar las preguntas y respuestas
def tokenize_function(examples):
    return tokenizer(examples["question"], examples["context"], truncation=True, padding="max_length", max_length=512)

tokenized_datasets = train_dataset.map(tokenize_function, batched=True)

# Configurar los parámetros de entrenamiento
training_args = TrainingArguments(
    output_dir='./results',          # Directorio donde guardar el modelo
    evaluation_strategy="epoch",     # Evaluar al final de cada época
    learning_rate=2e-5,              # Tasa de aprendizaje
    per_device_train_batch_size=8,   # Tamaño de lote
    num_train_epochs=3,              # Número de épocas
    weight_decay=0.01,               # Regularización L2
)

# Crear el objeto Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
    data_collator=None,  # Esto es opcional, solo si necesitas un collator específico
)

# Entrenar el modelo
trainer.train()
