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
    STATEMENTS = json.load(f)

# -----------------------------
# TELEGRAM APPLICATION
# -----------------------------
application = ApplicationBuilder().token(BOT_TOKEN).build()

# -----------------------------
# MESSAGE HANDLER
# -----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("MESSAGE RECEIVED:", update.message.text)
    await update.message.reply_text("Received.")

    user_text = update.message.text.lower()
    logger.info(f"Received: {user_text}")

    for item in STATEMENTS:
        keywords = [k.lower() for k in item.get("keywords", [])]
        question = item.get("question", "").lower()

        if any(k in user_text for k in keywords) or (question and question in user_text):
            await update.message.reply_text(item.get("answer", ""))
            logger.info(f"Matched: {item.get('question')}")
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