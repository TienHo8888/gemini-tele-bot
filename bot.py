import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# Lấy API key từ biến môi trường
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Cấu hình Gemini (API v1)
genai.configure(api_key=GOOGLE_API_KEY)

# Khởi tạo model Gemini Pro (chuẩn v1)
model = genai.GenerativeModel(
    model_name="models/gemini-2.0-flash",
    generation_config={
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 1024,
    }
)

# === XỬ LÝ TIN NHẮN ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào! Tôi là bot Gemini thân thiện, kiểu bạn bè vui tính. Cứ hỏi gì đi 😎"
    )
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_type = message.chat.type
    user_input = message.text
    bot_username = context.bot.username

    # Chỉ phản hồi nếu bị tag trong nhóm
    if chat_type in ["group", "supergroup"]:
        if f"@{bot_username}" not in user_input:
            return
        user_input = user_input.replace(f"@{bot_username}", "").strip()

    try:
        prompt = ( "Mày là một trợ lý AI kiểu bạn bè anh em, nói chuyện thẳng thắn, vui vẻ, không hoa mỹ. "
    "Nói ngắn gọn, dễ hiểu như đang ngồi nhậu với chiến hữu. Nếu được thì pha chút hài cũng ok.\n\n"
    f"Người dùng hỏi: {user_input}"
)
        response = model.generate_content(prompt)
        reply = response.text.strip()       
    except Exception as e:
        reply = f"❌ Lỗi gọi Gemini: {e}"

    await message.reply_text(reply)


# === MAIN ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot Gemini bạn bè đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()