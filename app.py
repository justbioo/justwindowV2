import os
import threading
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Настройки ---
TOKEN = os.environ.get("TELEGRAM_TOKEN", "9269273842:AAG5jd65Mh-JsC9CfyteINMZ8R2IZquDOts")
app = Flask(__name__)

# Хранилище кодов: { "код": {"id": 123, "username": "name", "confirmed": True} }
auth_codes = {}

# --- Логика бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args  # Сюда попадает код из ?start=КОД

    if not args:
        await update.message.reply_text("Привет! Открой ссылку из приложения HoverPanel.")
        return

    code = args[0]
    # Сохраняем связку кода и пользователя
    auth_codes[code] = {
        "id": user.id,
        "username": user.username if user.username else user.first_name,
        "confirmed": True
    }
    await update.message.reply_text(f"✅ Авторизация в HoverPanel подтверждена, {user.first_name}!")

# --- Flask API для WPF ---
@app.route("/check/<code>")
def check_code(code):
    data = auth_codes.get(code)
    if data and data.get("confirmed"):
        return jsonify({"status": "ok", "user": data})
    return jsonify({"status": "pending"})

@app.route("/health")
def health():
    return "OK"

# --- Запуск бота в фоне ---
def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке, чтобы Flask мог слушать порт
    threading.Thread(target=run_bot, daemon=True).start()
    # Render передает порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)