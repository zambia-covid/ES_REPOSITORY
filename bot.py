import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

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


# ---- Health Check ----
@app.get("/")
async def root():
    return {"status": "Bot is live"}


# ---- Webhook Route ----
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}
