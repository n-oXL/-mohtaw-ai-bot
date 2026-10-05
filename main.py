import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video = message.video or message.document
    
    if not video:
        await message.reply_text("أهلًا بك! أرسل ملف فيديو أو حلقة لنبدأ معالجتها وترجمتها.")
        return

    await message.reply_text("📥 جاري استلام الحلقة وبدء معالجة الترجمة... انتظر قليلاً.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    print("🤖 البوت يعمل الآن...")
    app.run_polling()

if __name__ == '__main__':
    main()
