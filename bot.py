import json
import logging
import os

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# -----------------------------
# CONFIG
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Ensure this is set in Render environment

# -----------------------------
# LOAD STATEMENTS
# -----------------------------
with open("statements.json", "r", encoding="utf-8") as f:
    repository = json.load(f)

    print("Repository loaded:", repository)

# -----------------------------
# TELEGRAM APPLICATION
# -----------------------------
application = ApplicationBuilder().token(BOT_TOKEN).build()

# -----------------------------
# MESSAGE HANDLER
# -----------------------------
repository = [
    {
        "keywords": ["hello", "hi"],
        "response": "Hello there!"
    },
    {
        "keywords": ["help"],
        "response": "How can I assist you?"
    }
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower()

    for item in repository:
        if any(keyword in text for keyword in item["keywords"]):
            await update.message.reply_text(item["response"])
            return
        
    await update.message.reply_text("That issue is not yet in my repository. It will be addressed.")

# Add handler
application.add_handler(MessageHandler(filters.TEXT, handle_message))

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI()

@app.on_event("startup")
async def startup():
    logger.info("Starting Telegram application...")
    await application.initialize()
    await application.start()

@app.on_event("shutdown")
async def shutdown():
    logger.info("Stopping Telegram application...")
    await application.stop()
    await application.shutdown()

@app.get("/")
async def root():
    return {"status": "Bot is running"}

@app.post("/{full_path:path}")
async def telegram_webhook(full_path: str, request: Request):

    data = await request.json()
    update = Update.de_json(data, application.bot)

    await application.process_update(update)

    return {"ok": True}