import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# ----------- إعدادات البوت -------------
BOT_TOKEN = "8258792690:AAH9QgR6epUv3zKyMFMUF48ZOUkKqRCcuTA"
DATA_FILE = "data.json"

# ----------- إعداد اللوق -------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------- الثوابت للمراحل -------------
(
    CHOOSING,
    UPLOAD_VIDEO,
    UPLOAD_URL,
    VIEW_VIDEO,
    EMBED_VIDEO,
    SHOW_VIDEO_LIST,
    SHOW_URL_LIST,
    DELETE_URL,
    STREAM_VIDEO,
    STREAM_VIDEO_LIST,
    EMBED_STREAM_LIST,
) = range(11)

# ----------- مفاتيح الأوامر (Reply Keyboard) -------------

reply_keyboard = [
    ['/start bot'],
    ['/upload video', '/upload video form url'],
    ['/view video', '/embed video'],
    ['/show video list', '/show url list'],
    ['/delete url from list'],
    ['/stream video', '/stream video list'],
    ['/embed stream vedio list'],
]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

# ----------- دوال قراءة وكتابة data.json -------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ----------- دوال مساعدة -------------

def ensure_user(data, user_id):
    if user_id not in data:
        data[user_id] = {
            "folders": {"default": []},
            "stream_links": [],
            "url_list": []
        }

# ----------- أوامر البوت -------------

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s started the bot.", user.id)
    update.message.reply_text(
        "Welcome to the Video Bot! Choose an option from the menu below:",
        reply_markup=markup,
    )
    return CHOOSING

# --- أرسل رسالة إذا أمر غير معروف ---
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry, I didn't understand that command. Please use the menu.")

# --- /upload video ---

def upload_video_start(update: Update, context: CallbackContext):
    update.message.reply_text("Please send me the video file to upload.", reply_markup=ReplyKeyboardRemove())
    return UPLOAD_VIDEO

def upload_video_receive(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = load_data()
    ensure_user(data, user_id)

    video_file = update.message.video or update.message.document
    if video_file is None:
        update.message.reply_text("This is not a video file. Please send a valid video.")
        return UPLOAD_VIDEO

    file_id = video_file.file_id
    file_name = video_file.file_name or "video.mp4"

    # حفظ الفيديو في المجلد الافتراضي data.json فقط (للتبسيط)
    folder = "default"
    data[user_id]["folders"].setdefault(folder, [])
    embed_code = f"#embed:{folder}/{file_name}"

    # تخزين بيانات الفيديو
    data[user_id]["folders"][folder].append({
        "name": file_name,
        "url": file_id,
        "embed_code": embed_code,
    })

    save_data(data)

    update.message.reply_text(f"Video saved under folder '{folder}'.\nEmbed code:\n{embed_code}")

    return start(update, context)

# --- /upload video form url ---

def upload_url_start(update: Update, context: CallbackContext):
    update.message.reply_text("Please send me the direct video URL (must end with .mp4, .webm, etc).", reply_markup=ReplyKeyboardRemove())
    return UPLOAD_URL

def upload_url_receive(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    user_id = str(update.message.from_user.id)
    data = load_data()
    ensure_user(data, user_id)

    # تحقق بسيط من الرابط
    if not (url.startswith("http://") or url.startswith("https://")) or not any(url.endswith(ext) for ext in [".mp4", ".webm", ".mov", ".mkv"]):
        update.message.reply_text("Invalid URL or unsupported video format. Please send a direct video URL ending with .mp4, .webm, .mov, or .mkv.")
        return UPLOAD_URL

    folder = "default"
    data[user_id]["folders"].setdefault(folder, [])

    file_name = url.split("/")[-1]

    embed_code = f"#embed:{folder}/{file_name}"

    # تخزين الرابط في المجلد
    data[user_id]["folders"][folder].append({
        "name": file_name,
        "url": url,
        "embed_code": embed_code,
    })

    # حفظ أيضا في url_list
    if url not in data[user_id]["url_list"]:
        data[user_id]["url_list"].append(url)

    save_data(data)

    update.message.reply_text(f"Video URL saved under folder '{folder}'.\nEmbed code:\n{embed_code}")

    return start(update, context)

# --- /show video list ---

def show_video_list(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = load_data()
    ensure_user(data, user_id)

    folders = data[user_id]["folders"]

    text = "🎞️ Your Videos:\n"
    for folder_name, videos in folders.items():
        text += f"\n📁 Folder: {folder_name} ({len(videos)} videos)\n"
        for i, v in enumerate(videos, 1):
            text += f"  {i}. {v['name']}\n"

    update.message.reply_text(text or "You have no videos saved.")

    return CHOOSING

# --- /show url list ---

def show_url_list(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = load_data()
    ensure_user(data, user_id)

    urls = data[user_id]["url_list"]

    if not urls:
        update.message.reply_text("You have no saved URLs.")
    else:
        text = "🔗 Saved URLs:\n"
        for i, url in enumerate(urls, 1):
            text += f"{i}. {url}\n"
        update.message.reply_text(text)

    return CHOOSING

# --- /delete url from list ---

def delete_url_start(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = load_data()
    ensure_user(data, user_id)

    urls = data[user_id]["url_list"]
    if not urls:
        update.message.reply_text("No URLs to delete.")
        return CHOOSING

    text = "Send the number of the URL you want to delete:\n"
    for i, url in enumerate(urls, 1):
        text += f"{i}. {url}\n"

    update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return DELETE_URL

def delete_url_receive(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = load_data()

    try:
        index = int(update.message.text.strip()) - 1
    except ValueError:
        update.message.reply_text("Please send a valid number.")
        return DELETE_URL

    urls = data[user_id]["url_list"]

    if 0 <= index < len(urls):
        removed = urls.pop(index)
        save_data(data)
        update.message.reply_text(f"Removed URL:\n{removed}")
    else:
        update.message.reply_text("Invalid number.")

    return start(update, context)

# --- /embed video (يعرض كود التضمين للفيديو الأخير في default) ---

def embed_video(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    data = load_data()
    ensure_user(data, user_id)

    videos = data[user_id]["folders"].get("default", [])
    if not videos:
        update.message.reply_text("No videos found to embed.")
    else:
        last_video = videos[-1]
        update.message.reply_text(f"Embed code:\n{last_video['embed_code']}")

    return CHOOSING

# --- /stream video ---

def stream_video(update: Update, context: CallbackContext):
    update.message.reply_text("This feature is not implemented yet. Coming soon!")
    return CHOOSING

# --- /stream video list ---

def stream_video_list(update
