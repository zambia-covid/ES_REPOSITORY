import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================
# CONFIG
# ==========================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # replace with your bot token
PORT = 8000  # default FastAPI port, Render overrides with $PORT

# ==========================
# LOGGING
# ==========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================
# TELEGRAM BOT SETUP
# ==========================
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am live and ready to answer your questions.")

# Text handler
async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"Incoming message from {update.effective_user.id}: {user_text}")

    # Simple logic for demo purposes
    if "hello" in user_text.lower():
        reply = "Hi there! How can I help you today?"
    else:
        reply = f"You said: {user_text}"

    await update.message.reply_text(reply)
    logger.info(f"Sent reply to {update.effective_user.id}: {reply}")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

# ==========================
# FASTAPI SETUP
# ==========================
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot is live!"}

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    """Webhook endpoint to receive Telegram updates."""
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}
    except Exception as e:
        logger.exception("Error processing update")
        return {"ok": False, "error": str(e)}

# ==========================
# START BOT (OPTIONAL LOCAL TEST)
# ==========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT, log_level="info")
