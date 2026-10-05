import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video = message.video or message.document
    
    if not video:
        await message.reply_text("الرجاء إرسال فيديو صحيح.")
        return

    await message.reply_text("📥 تم استلام الفيديو بنجاح، البوت يعمل الآن بشكل مستقر وممتاز!")

async def main():
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على TELEGRAM_BOT_TOKEN")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("🤖 البوت يعمل الآن ويستمع للفيديوهات...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # يبقي البوت شغّالاً
    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    asyncio.run(main())
