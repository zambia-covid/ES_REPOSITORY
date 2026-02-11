import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

application = ApplicationBuilder().token(BOT_TOKEN).build()

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot connected successfully.")

application.add_handler(CommandHandler("start", start))

# ---- Initialize Telegram App Properly ----
async def init_app():
    await application.initialize()
    await application.start()

asyncio.get_event_loop().run_until_complete(init_app())

# ---- Routes ----
@app.route("/")
def home():
    return "Bot is live"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"
