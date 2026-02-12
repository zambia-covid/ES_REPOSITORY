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
  
# -----------------------------
# TELEGRAM APPLICATION
# -----------------------------
application = ApplicationBuilder().token(BOT_TOKEN).build()

# -----------------------------
# MESSAGE HANDLER
# -----------------------------

def score_match(user_text, question_text):
    user_words = set(user_text.split())
    question_words = set(question_text.split())
    return len(user_words & question_words)

best_match = None
best_score = 0

for item in data:
    score = score_match(text, item.get("question", "").lower())
    if score > best_score:
        best_score = score
        best_match = item

if best_score > 2:
    await update.message.reply_text(best_match["answer"])
else:
    await update.message.reply_text("No matching doctrine found.")
    )

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