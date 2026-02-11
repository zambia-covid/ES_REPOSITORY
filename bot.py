from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is live and responding.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f"You asked: {user_text}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Startup & Shutdown ---

@app.on_event("startup")
async def startup():
    await application.initialize()

@app.on_event("shutdown")
async def shutdown():
    await application.shutdown()

# --- Webhook ---

@app.post("/{full_path:path}")
async def telegram_webhook(full_path: str, request: Request):
    if full_path != BOT_TOKEN:
        return {"error": "Invalid webhook path"}

    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)

    return {"ok": True}