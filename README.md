# Telegram Video Bot 🎥🤖

This is a personal Telegram bot that downloads direct video links (e.g. `.mp4`, `.webm`) and uploads them directly to your Telegram saved messages (Telegram cloud).

## 🔧 Features

- Accepts direct video URLs (.mp4, .webm, etc.)
- Downloads the video
- Uploads it to your private chat with the bot (your Telegram cloud)
- Saves the link in a memory list for future use
- Commands:
  - `/start` – Welcome message
  - `/list` – List saved video URLs
  - `/delete [n]` – Delete a specific URL
  - `/clear` – Clear all saved URLs

## ⚙️ Requirements

- Python 3.9+
- `python-telegram-bot`
- `requests`

## 🚀 Running Locally

```bash
pip install -r requirements.txt
python tp.py
