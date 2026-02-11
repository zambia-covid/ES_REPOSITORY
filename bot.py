import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

app = FastAPI()

application = ApplicationBuilder().token(BOT_TOKEN).build()

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot connected successfully.")

application.add_handler(CommandHandler("start", start))

# ---- Startup Event ----
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()
    logging.info("Bot initialized and started")


# ---- Health Check ----
@app.get("/")
async def root():
    return {"status": "Bot is live"}


# ---- Webhook Route ----
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return {"ok": True}
    except Exception as e:
        logging.exception("Failed to process update")
        # Always return {"ok": True} even on errors so Telegram stops retrying endlessly
        return {"ok": True}
