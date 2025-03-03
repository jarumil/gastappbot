import telegram
import os
import constants.constants as cts
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import re
from utils import get_class_from_string, download_page_in_pdf
from nlp.nlp import NLP as NLPClass
from voice.voicetotext import VoiceToText as VoiceToTextAbstract
import asyncio
from oauth2client.service_account import ServiceAccountCredentials


with open("config.json", "r") as f:
    config = json.load(f)

VoiceToTextClass = get_class_from_string(config["voice"])

with open(os.path.join(cts.CREDENTIALS_FOLDER, cts.API_CREDENTIALS_FILE), 'r') as file:
        api_credentials = json.load(file)

NLP = NLPClass()
VOICE: VoiceToTextAbstract = VoiceToTextClass()
TOKEN = api_credentials["telegram"]
SHEET_ID = api_credentials["spreadsheet_id"]
GID = api_credentials["spreadsheet_dashboard_guid"]
GSCREDENTIALS = ServiceAccountCredentials.from_json_keyfile_name(
    os.path.join(cts.CREDENTIALS_FOLDER, cts.CREDENTIALS_FILE),
    ['https://spreadsheets.google.com/feeds'],
)
bot = telegram.Bot(token=TOKEN)

def message_is_ready(message, previous_message):
    """
    Check if the message is ready to be processed.

    Parameters
    ----------
    message : str
        The current message.
    previous_message : str
        The previous message.

    Returns
    -------
    bool
        True if the message is ready to be processed, False otherwise.
    """
    process_message = '[DONE]' not in message
    process_message = process_message and message != previous_message
    process_message = process_message and message != ''
    return process_message

def escape_markdown_v2(text):
    """
    Escape special characters for MarkdownV2.

    Parameters
    ----------
    text : str
        The text to be escaped.

    Returns
    -------
    str
        The escaped text.
    """
    escape_chars = r'_[]()~`>#+-=|{}.!'
    
    new_text = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    return new_text.replace('**', '*')

async def send_response_progressively(chat_id, sent_msg, question, parse_mode=None):
    """
    Send the response progressively to the user.

    Parameters
    ----------
    chat_id : int
        The chat ID to send the response to.
    sent_msg : telegram.Message
        The message object of the sent message.
    question : str
        The question to generate a response for.
    parse_mode : str, optional
        The parse mode for the message (default is None).

    Returns
    -------
    None
    """
    response_text = ""
    previous_message = ""
    num_new_characters = 50
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
                if (new_characters > num_new_characters):
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
                    await asyncio.sleep(0.5)
                new_characters += 1
        except telegram.error.RetryAfter as e:
            print(f"Waiting {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)
        except telegram.error.BadRequest as e:
            await asyncio.sleep(1)
            continue
    
    # Send the final message
    while True:
        try:
            await bot.send_chat_action(chat_id, "typing")
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=sent_msg.message_id,
                text=response_text,
                parse_mode=parse_mode,
            )
            break
        except telegram.error.RetryAfter as e:
            print(f"Waiting {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)
        except telegram.error.BadRequest as e:
            print(f"Error: {e}")
            break

async def start(update: Update, context):
    """
    Handle the /start command.

    Parameters
    ----------
    update : telegram.Update
        The update object.
    context : telegram.ext.CallbackContext
        The callback context.

    Returns
    -------
    None
    """
    await update.message.reply_text(
        "¡Hola! Soy un bot que puede responder tus preguntas."
        "Puedes enviarme un mensaje de voz o texto y te responderé lo mejor que pueda."
    )

async def handle_audio(update: Update, context):
    """
    Handle audio messages.

    Parameters
    ----------
    update : telegram.Update
        The update object.
    context : telegram.ext.CallbackContext
        The callback context.

    Returns
    -------
    None
    """
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
    """
    Handle text messages.

    Parameters
    ----------
    update : telegram.Update
        The update object.
    context : telegram.ext.CallbackContext
        The callback context.

    Returns
    -------
    None
    """
    question = update.message.text 
    chat_id = update.message.chat.id
    message_id = update.message.message_id

    await bot.send_chat_action(chat_id, "typing")

    sent_msg = await bot.send_message(chat_id, escape_markdown_v2("..."), parse_mode="MarkdownV2")

    await send_response_progressively(chat_id, sent_msg, question, parse_mode="MarkdownV2")

    print("Ready!")

async def download_dashboard(update: Update, context):
    """
    Download a dashboard in PDF format.

    Parameters
    ----------
    update : telegram.Update
        The update object.
    context : telegram.ext.CallbackContext
        The callback context.
    """
    chat_id = update.message.chat.id
    await bot.send_chat_action(chat_id, "upload_document")

    filename = download_page_in_pdf(GSCREDENTIALS, SHEET_ID, GID)

    if filename:
        await bot.send_document(chat_id, open(filename, 'rb'))
        os.remove(filename)
        print("Ready!")
    else:
        await bot.send_message(chat_id, "No se pudo descargar el dashboard.")
        print("Ready! (Failed)")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dashboard", download_dashboard))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))

    application.run_polling()