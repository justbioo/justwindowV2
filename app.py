import os
import json
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN", "9269273842:AAG5jd65Mh-JsC9CfyteINMZ8R2IZquDOts")
WEBHOOK_SECRET = "hover_secret_123" # Придумай свое слово
RENDER_URL = "https://justwindowv2.onrender.com"

# Хранилище кодов (в памяти)
auth_codes = {}

# Инициализируем приложение Telegram
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

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

application.add_handler(CommandHandler("start", start))

@app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    """Telegram будет присылать сюда сообщения"""
    if request.method == "POST":
        # Передаем обновление в обработчик
        update = Update.de_json(request.get_json(force=True), application.bot)
        # Запускаем обработку асинхронно
        application.create_task(application.process_update(update))
        return "OK", 200
    return "Method Not Allowed", 405

@app.route("/set_webhook")
def set_webhook():
    """Вызови этот адрес ОДИН РАЗ в браузере, чтобы включить вебхук"""
    import requests
    url = f"{RENDER_URL}/webhook/{WEBHOOK_SECRET}"
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={url}")
    return response.json()

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
