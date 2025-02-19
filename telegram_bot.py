import telegram
import os
import constants.constants as cts
import json
import time 
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from nlp import generate_response  # Importamos la función desde nlp.py


with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE), 'r') as file:
        api_credentials = json.load(file)

# Configuración del token del bot de Telegram
TOKEN = api_credentials["telegram"]
bot = telegram.Bot(token=TOKEN)

def message_is_ready(message, previous_message):
    process_message = '[DONE]' not in message
    process_message = process_message and message != previous_message
    process_message = process_message and message != ''
    return process_message

def format_text(text):
    new_text = text.replace('**', '*')

    return new_text

# Función que se llama para enviar las respuestas al chat de Telegram
async def send_response_progressively(chat_id, sent_msg, question, parse_mode=None):
    """
    Esta función envía la respuesta de manera progresiva, actualizando el mensaje en el chat de Telegram.
    """
    response_text = ""
    previous_message = ""
    num_new_characters = 30
    new_characters = -1
    # Generamos la respuesta en streaming desde nlp.py
    for chunk in generate_response(question):
        try:
            response_text += chunk
        except TypeError:
            continue
        try:
            if message_is_ready(response_text, previous_message):
                if (new_characters > num_new_characters) or ("error" in response_text):
                    await bot.send_chat_action(chat_id, "typing")
                    await bot.edit_message_text(chat_id=chat_id, message_id=sent_msg.message_id, text=response_text)
                    previous_message = response_text
                    new_characters = -1
                    # Pausa para simular que el bot está escribiendo
                    time.sleep(0.5)
                new_characters += 1
        except telegram.error.RetryAfter as e:
            time.sleep(e.retry_after)
    
    # Enviamos el mensaje final
    await bot.send_chat_action(chat_id, "typing")
    await bot.edit_message_text(chat_id=chat_id, message_id=sent_msg.message_id, text=response_text)

# Comando para iniciar la interacción
async def start(update, context):
    await update.message.reply_text('¡Hola! Hazme una *pregunta* y te **responderé** en tiempo real.', parse_mode="Markdown")

# Comando para manejar la pregunta del usuario
async def handle_question(update, context):
    question = update.message.text  # Obtener la pregunta del usuario
    chat_id = update.message.chat.id  # ID del chat
    message_id = update.message.message_id  # ID del mensaje (para editar)

    # Mostrar acción de "escribiendo..." en Telegram
    await bot.send_chat_action(chat_id, "typing")

    # Enviar un mensaje inicial vacío
    sent_msg = await bot.send_message(chat_id, "...")

    # Llamamos a la función send_response_progressively para enviar la respuesta progresivamente
    await send_response_progressively(chat_id, sent_msg, question)

    print("Listo!")

if __name__ == '__main__':
    # Configura el bot
    application = Application.builder().token(TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    # Empezar el bot
    application.run_polling()