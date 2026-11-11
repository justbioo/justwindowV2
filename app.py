import os
import threading
import asyncio
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Настройки ---
TOKEN = os.environ.get("TELEGRAM_TOKEN", "9269273842:AAG5jd65Mh-JsC9CfyteINMZ8R2IZquDOts")
app = Flask(__name__)

# Хранилище кодов
auth_codes = {}

# --- Логика бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args  # Сюда попадает код из ?start=КОД

    if not args:
        await update.message.reply_text("Привет! Открой ссылку из приложения HoverPanel (кнопка Профиль).")
        return

    code = args[0]
    auth_codes[code] = {
        "id": user.id,
        "username": user.username if user.username else user.first_name,
        "confirmed": True
    }
    await update.message.reply_text(f"✅ Авторизация в HoverPanel подтверждена, {user.first_name}!")

# --- Запуск бота (правильный для Linux/Render) ---
def run_bot():
    # Создаем новый event loop для этого потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Бот запущен и слушает Telegram...")
    application.run_polling()

# --- Flask API ---
@app.route("/check/<code>")
def check_code(code):
    data = auth_codes.get(code)
    if data and data.get("confirmed"):
        return jsonify({"status": "ok", "user": data})
    return jsonify({"status": "pending"})

@app.route("/health")
def health():
    return "OK"

if __name__ == "__main__":
    # Запускаем бота
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
