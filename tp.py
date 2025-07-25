import logging
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Update
import os
import tempfile

# Logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# بيانات البوت
BOT_TOKEN = "8258792690:AAH9QgR6epUv3zKyMFMUF48ZOUkKqRCcuTA"
CHAT_ID = 5424440448

# ذاكرة مؤقتة لحفظ الروابط
video_links = []

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    await update.message.reply_text("👋 Send me a direct video link (.mp4, .webm, etc), and I’ll download & upload it here.")

# تحميل ورفع الفيديو
async def handle_video_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return

    url = update.message.text.strip()

    if not url.startswith("http") or not url.endswith(('.mp4', '.webm', '.mov', '.mkv', '.avi')):
        await update.message.reply_text("⚠️ Please send a valid direct video link (ending in .mp4, etc).")
        return

    await update.message.reply_text("⏬ Downloading video...")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # استخراج اسم الملف
        filename = url.split("/")[-1]
        if not filename:
            filename = "video.mp4"

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        # رفع الفيديو إلى دردشة البوت (Telegram Cloud)
        await update.message.reply_video(
            video=open(tmp_path, 'rb'),
            caption=f"🎥 Uploaded: {filename}"
        )

        video_links.append(url)
        await update.message.reply_text("✅ Video uploaded and saved. Use /list to view all saved links.")

        os.remove(tmp_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to download or send video:\n{e}")

# عرض القائمة
async def list_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    if not video_links:
        await update.message.reply_text("📂 Your video list is empty.")
    else:
        msg = "🎞️ Your saved videos:\n\n"
        for i, link in enumerate(video_links, start=1):
            msg += f"{i}. {link}\n"
        await update.message.reply_text(msg)

# حذف رابط من القائمة
async def delete_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usage: /delete [number] — e.g., /delete 2")
        return
    index = int(context.args[0]) - 1
    if 0 <= index < len(video_links):
        removed = video_links.pop(index)
        await update.message.reply_text(f"🗑️ Removed:\n{removed}")
    else:
        await update.message.reply_text("❌ Invalid number. Use /list to see correct indexes.")

# مسح القائمة
async def clear_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    video_links.clear()
    await update.message.reply_text("🧹 All saved links cleared.")

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_links))
    app.add_handler(CommandHandler("delete", delete_link))
    app.add_handler(CommandHandler("clear", clear_links))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_link))

    print("🚀 Bot is running. You can now send video links to it.")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")
