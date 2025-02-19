import telegram
import os
import constants.constants as cts
import json
import time 
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from nlp import generate_response  # Importamos la función desde nlp.py
from voicetotext import transcribe
import re


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

def escape_markdown_v2(text):
    # Caracteres especiales que deben escaparse en MarkdownV2
    escape_chars = r'_[]()~`>#+-=|{}.!'
    
    # Escapa cada uno de los caracteres especiales
    new_text = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    return new_text.replace('**', '*')

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
            if 'MarkdownV2' in parse_mode:
                chunk = escape_markdown_v2(chunk)
            response_text += chunk
        except TypeError:
            continue
        try:
            if message_is_ready(response_text, previous_message):
                if (new_characters > num_new_characters) or ("error" in response_text):
                    await bot.send_chat_action(chat_id, "typing")
                    await bot.edit_message_text(chat_id=chat_id, message_id=sent_msg.message_id, text=response_text, parse_mode=parse_mode)
                    previous_message = response_text
                    new_characters = -1
                    # Pausa para simular que el bot está escribiendo
                    time.sleep(0.5)
                new_characters += 1
        except telegram.error.RetryAfter as e:
            print(f"Esperando {e.retry_after} segundos...")
            time.sleep(e.retry_after)
        except telegram.error.BadRequest as e:
            continue
    
    # Enviamos el mensaje final
    await bot.send_chat_action(chat_id, "typing")
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=sent_msg.message_id, text=response_text, parse_mode=parse_mode)
    except telegram.error.BadRequest as e:
        pass

# Comando para iniciar la interacción
async def start(update: Update, context):
    await update.message.reply_text(escape_markdown_v2("¡Hola! Soy un bot que puede responder tus preguntas. *Puedes* enviarme un mensaje de voz o texto y te **responderé** lo mejor que pueda."), parse_mode="MarkdownV2")

async def handle_audio(update: Update, context):
    chat_id = update.message.chat.id
    file_id = update.message.voice.file_id if update.message.voice else update.message.audio.file_id
    new_file = await context.bot.get_file(file_id)

    await bot.send_chat_action(chat_id, "typing")

    # Enviar un mensaje inicial vacío
    sent_msg = await bot.send_message(chat_id, escape_markdown_v2("..."), parse_mode="MarkdownV2")

    audio_path = f"temp_audio.ogg"
    await new_file.download_to_drive(audio_path)

    transcribed_text = transcribe(audio_path)
    os.remove(audio_path)

    await send_response_progressively(chat_id, sent_msg, transcribed_text, parse_mode="MarkdownV2")

    print("Listo!")

# Comando para manejar la pregunta del usuario
async def handle_question(update: Update, context):
    question = update.message.text  # Obtener la pregunta del usuario
    chat_id = update.message.chat.id  # ID del chat
    message_id = update.message.message_id  # ID del mensaje (para editar)

    # Mostrar acción de "escribiendo..." en Telegram
    await bot.send_chat_action(chat_id, "typing")

    # Enviar un mensaje inicial vacío
    sent_msg = await bot.send_message(chat_id, escape_markdown_v2("..."), parse_mode="MarkdownV2")

    # Llamamos a la función send_response_progressively para enviar la respuesta progresivamente
    await send_response_progressively(chat_id, sent_msg, question, parse_mode="MarkdownV2")

    print("Listo!")

if __name__ == '__main__':
    # Configura el bot
    application = Application.builder().token(TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    # Empezar el bot
    application.run_polling()