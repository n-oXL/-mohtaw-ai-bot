import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context):
    await update.message.reply_text("شغال البوت معاك زي الحلاوة 🚀")

async def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على التوكن")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("البوت يعمل الآن...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    asyncio.run(main())
