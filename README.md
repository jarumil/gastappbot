
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

---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gastappbot.git
   cd gastappbot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   `conda create --name [NAME] python=3.11
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
     "telegram": "your_bot_key"
   }
   ```

2. **Spreadsheet credentials:**  
   Create `credentials.json` file in the `credentials/` folder.

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
  ├── /credentials           # Folder to store the credentials
  ├── /data                  # Folder to store the data
  ├── /databk                # Folder to store the old data as backup
  ├── /logs                  # Folder to store the logs
  ├── /results               # Folder to store the results
  ├── telegram_bot.py        # Main script for the Telegram bot
  ├── nlp.py                 # Logic to generate responses using the API
  ├── prompt.py              # Script to generate the prompt engineering
  ├── update_data.py         # Script to update the data
  ├── voice_to_text.py       # Script to process the voice messages
  ├── requirements.txt       # Project dependencies
  └── README.md              # This documentation file
```

---

## 📄 License

This project is licensed under the GPL License. See the [LICENSE](LICENSE) file for details.
