# GastappBot: Telegram Bot for Expense Management

This repository contains a Telegram bot called **GastappBot** that interacts with an expense management system. The bot allows users to ask questions about their expenses and receives progressive responses, mimicking a more conversational flow.

---

## 🚀 Features

- **Expense Management:** You can easily query details about your expenses.
- **Progressive Responses:** The bot simulates an interactive conversation by showing responses in real-time, with the bot "typing..." during the conversation.
- **External API Integration:** The bot generates responses from an API configured in a JSON file.

---

## 🛠️ Requirements

Make sure you have the following installed:

- **Python 3.11+**  
- **Required libraries:**
  - `gspread`
  - `oauth2client`
  - `pandas`
  - `typer`
  - `python-telegram-bot`
  - `openai-whisper`
  - `ffmpeg-python`

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gastappbot.git
   cd gastappbot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   conda create --name [NAME] python=3.11
   conda activate [NAME]
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 Configuration

1. **API Keys:**  
   Create `api_credentials.json` file in the `credentials/` folder with the following format:

   ```json
   {
     "openrouter_key": "your_api_key",
     "telegram": "your_bot_key",
     "spreadsheet_id": "your_spreadsheet_id"
   }
   ```

2. **Spreadsheet credentials:**  
   Create `credentials.json` file in the `credentials/` folder (see [info](https://developers.google.com/workspace/guides/create-credentials)).

3. **Specify your personal configuration:**  
   Update the `config.json` file in the root directory with your specific configuration details. The file should include the following fields:
   - `sheet_data_name`: The name of the sheet in your spreadsheet where the data is stored.
   - `data`: The path to the data class used for prompt generation.
   - `voice`: The path to the voice-to-text processing class.
   - `question`: The template for formatting questions.
   - `prompt`: The template for generating the prompt used by the bot.

   Example `config.json`:
   ```json
   {
       "sheet_data_name": "Datos",
       "data": "prompt.data.MyData",
       "voice": "voice.voicetotext.WhisperVoiceToText",
       "openrouter_models": [
         {"name": "deepseek/deepseek-r1:free"},
         {"name": "deepseek/deepseek-chat:free"}
       ],
       "question": "Pregunta: {question}.",
       "prompt": "..."
   }
   ```
   You can create new voice models, nlp models and data loaders in the corresponding folders and use them modifying the `config.json` file.

---

## 📝 Usage

1. **Set up the Telegram Bot:**  
   Create a bot on Telegram using [BotFather](https://core.telegram.org/bots#botfather) and get your **token** (update the `api_credentials.json` file).

2. **Update the data:**  
   ```bash
   python update_data.py
   ```

3. **Run the bot:**  
   To start the bot, run the following command:

   ```bash
   python telegram_bot.py
   ```

4. **Interact with the bot:**  
   On Telegram, search for your bot and start chatting with it by asking questions related to your expenses.

---

## 📚 Project Structure

The repository contains the following folders and files:

```
/gastappbot
  ├── /constants             # Folder for the constants
      └── constants.py
  ├── /prompt                # Folder for prompt engineering
      ├── data.py
      └── prompt.py
  ├── /nlp                   # Folder for nlp processing
      ├── models.py
      └── nlp.py
  ├── /voice                 # Folder for voice processing
      └── voicetotext.py
  ├── telegram_bot.py        # Main script for the Telegram bot
  ├── update_data.py         # Script to update the data
  ├── config.json            # Configuration file
  ├── requirements.txt       # Project dependencies
  ├── LICENSE                # License
  └── README.md              # This documentation file
```

---

## 🧑‍🤝‍🧑 Contributing

1. **Fork** the repository.
2. Create a branch (`git checkout -b new-feature`).
3. Make your changes and commit (`git commit -am 'Add new feature'`).
4. Push your changes (`git push origin new-feature`).
5. Open a **pull request**.

---

## 📄 License

This project is licensed under the GPL License. See the [LICENSE](LICENSE) file for details.
