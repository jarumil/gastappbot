import telegram
import os
import constants.constants as cts
import json
import time 
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import re
from utils import get_class_from_string
from nlp.nlp import NLP as NLPClass
from voice.voicetotext import VoiceToText as VoiceToTextAbstract


with open("config.json", "r") as f:
    config = json.load(f)

VoiceToTextClass = get_class_from_string(config["voice"])

with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE), 'r') as file:
        api_credentials = json.load(file)

NLP = NLPClass()
VOICE: VoiceToTextAbstract = VoiceToTextClass()
TOKEN = api_credentials["telegram"]
bot = telegram.Bot(token=TOKEN)

def message_is_ready(message, previous_message):
    process_message = '[DONE]' not in message
    process_message = process_message and message != previous_message
    process_message = process_message and message != ''
    return process_message

def escape_markdown_v2(text):
    escape_chars = r'_[]()~`>#+-=|{}.!'
    
    new_text = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    return new_text.replace('**', '*')

async def send_response_progressively(chat_id, sent_msg, question, parse_mode=None):
    """
    This function sends the response progressively to the user.
    """
    response_text = ""
    previous_message = ""
    num_new_characters = 30
    new_characters = -1

    for chunk in NLP.generate_response(question):
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
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=sent_msg.message_id,
                        text=response_text,
                        parse_mode=parse_mode,
                    )
                    previous_message = response_text
                    new_characters = -1

                    # Pause for a moment to avoid hitting the rate limit
                    time.sleep(0.5)
                new_characters += 1
        except telegram.error.RetryAfter as e:
            print(f"Waiting {e.retry_after} seconds...")
            time.sleep(e.retry_after)
        except telegram.error.BadRequest as e:
            continue
    
    # Send the final message
    await bot.send_chat_action(chat_id, "typing")
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=sent_msg.message_id,
            text=response_text,
            parse_mode=parse_mode,
        )
    except telegram.error.BadRequest as e:
        pass

async def start(update: Update, context):
    await update.message.reply_text(
        "¡Hola! Soy un bot que puede responder tus preguntas."
        "Puedes enviarme un mensaje de voz o texto y te responderé lo mejor que pueda."
    )

async def handle_audio(update: Update, context):
    chat_id = update.message.chat.id
    file_id = update.message.voice.file_id if update.message.voice else update.message.audio.file_id
    new_file = await context.bot.get_file(file_id)

    await bot.send_chat_action(chat_id, "typing")

    sent_msg = await bot.send_message(chat_id, escape_markdown_v2("..."), parse_mode="MarkdownV2")

    audio_path = f"temp_audio.ogg"
    await new_file.download_to_drive(audio_path)

    transcribed_text = VOICE.transcribe(audio_path)
    os.remove(audio_path)

    await send_response_progressively(chat_id, sent_msg, transcribed_text, parse_mode="MarkdownV2")

    print("Ready!")

async def handle_question(update: Update, context):
    question = update.message.text 
    chat_id = update.message.chat.id
    message_id = update.message.message_id

    await bot.send_chat_action(chat_id, "typing")

    sent_msg = await bot.send_message(chat_id, escape_markdown_v2("..."), parse_mode="MarkdownV2")

    await send_response_progressively(chat_id, sent_msg, question, parse_mode="MarkdownV2")

    print("Ready!")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    application.run_polling()