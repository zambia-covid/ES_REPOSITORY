import json
import logging
import os

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# -----------------------------
# BASIC CONFIG
# -----------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set this in Render Environment

# -----------------------------
# LOAD STATEMENTS
# -----------------------------

with open("statements.json", "r", encoding="utf-8") as f:
    STATEMENTS = json.load(f)

# -----------------------------
# CREATE TELEGRAM APPLICATION
# -----------------------------

application = ApplicationBuilder().token(BOT_TOKEN).build()

# -----------------------------
# MESSAGE HANDLER
# -----------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.lower()

    for item in STATEMENTS:

        # Tag matching
        if any(tag.lower() in user_text for tag in item.get("tags", [])):
            await update.message.reply_text(item["answer"])
            return

        # Partial keyword matching from question
        question_words = item["question"].lower().split()
        if any(word in user_text for word in question_words if len(word) > 4):
            await update.message.reply_text(item["answer"])
            return

    await update.message.reply_text(
        "That issue is not yet in the repository."
    )

# Add handler AFTER defining function
application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI()


@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()


@app.on_event("shutdown")
async def shutdown():
    await application.stop()
    await application.shutdown()


@app.get("/")
async def root():
    return {"status": "Bot is running"}


@app.post("/{full_path:path}")
async def telegram_webhook(full_path: str, request: Request):
    # Accept both encoded and non-encoded token
    if full_path != BOT_TOKEN:
        return {"error": "Invalid webhook path"}

    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.exception("Error processing update")
        return {"ok": False, "error": str(e)}