
from flask import Flask
import threading

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "✅ Bot Telegram đang hoạt động!"

def keep_alive():
    web_app.run(host="0.0.0.0", port=8080)



import logging
import asyncio
import json
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask
import threading
# Load scripts.json nếu có
try:
    with open("scripts.json", "r", encoding="utf-8") as f:
        special_scripts = json.load(f)
except FileNotFoundError:
    special_scripts = {}

# Ghi nhớ context hội thoại
context_memory = {}

# Ghi log UX
def log_chat(user_id, user_input, bot_output):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user_id}: {user_input} → {bot_output}\n")

# Ghi nhận câu hỏi chưa biết
def record_unknown_question(question: str):
    with open("unknown_questions.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {question.strip()}\n")

# Trả lời đặc biệt theo scripts.json
def check_special_response(user_input, script_dict):
    for keyword, response in script_dict.items():
        if keyword.lower() in user_input.lower():
            return response
    return None

# Mô phỏng tìm kiếm web bằng Serper.dev
def google_search(query):
    api_key = "YO9bef194a8499575861964afe4f816df9387729a0"  # 👈 Thay bằng key thật nếu dùng
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key}
    data = {"q": query}

    try:
        res = requests.post(url, headers=headers, json=data)
        result = res.json()
        return result["organic"][0]["snippet"] if result["organic"] else "Không tìm thấy kết quả."
    except:
        return "Lỗi khi tìm kiếm thông tin từ web."

# Gọi Gemini hoặc giả lập
async def get_gemini_response(prompt: str):
    now = datetime.now().strftime("%H:%M ngày %d/%m/%Y")
    full_prompt = f"Hôm nay là {now}. Hãy trả lời một cách tự nhiên nhé.\n{prompt}"
    return f"[Giả lập trả lời] {full_prompt[-100:]}"  # Thay bằng API call thật nếu cần

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Xin chào! Tôi là bot thông minh của Tiho. Hỏi gì cũng chơi, nhớ luôn cả cuộc trò chuyện đó nha!")

# Xử lý tin nhắn
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        return

    user_id = update.effective_user.id
    user_input = message.text.strip()

    # Nếu có trong scripts
    special_reply = check_special_response(user_input, special_scripts)
    if special_reply:
        await message.reply_text(special_reply)
        log_chat(user_id, user_input, special_reply)
        return

    # Ghi nhớ context hội thoại
    if user_id not in context_memory:
        context_memory[user_id] = []
    context_memory[user_id].append(f"User: {user_input}")
    if len(context_memory[user_id]) > 6:
        context_memory[user_id] = context_memory[user_id][-6:]

    # Nếu phát hiện muốn tra Google
    if any(keyword in user_input.lower() for keyword in ["tra google", "google", "là gì", "tra cứu"]):
        info = google_search(user_input)
        context_memory[user_id].append(f"Bot: {info}")
        await message.reply_text(info)
        log_chat(user_id, user_input, info)
        return

    # Trả lời bằng AI
    context_text = "\n".join(context_memory[user_id])
    response = await get_gemini_response(context_text)
    context_memory[user_id].append(f"Bot: {response}")
    if response.strip() != user_input.strip():
        await message.reply_text(response)
    log_chat(user_id, user_input, response)
    record_unknown_question(user_input)

# Khởi chạy bot
def home():
    return "✅ Bot Telegram đang hoạt động!"

def keep_alive():
    web_app.run(host="0.0.0.0", port=8080)
def main():
    threading.Thread(target=keep_alive).start()
    import os

    # 👉 Gọi Flask giữ port sống
    threading.Thread(target=keep_alive).start()

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot đang chạy (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
