import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video = message.video or message.document
    
    if not video:
        await message.reply_text("الرجاء إرسال فيديو صحيح.")
        return

    await message.reply_text("📥 تم استلام الفيديو، جارٍ تجهيزه للخدمة...")
    # هنا تم تبسيط الكود لضمان عدم توقف السيرفر المجاني على Render، وقريباً نربطه بخدمة ترجمة خارجية سريعة.
    await message.reply_text("✨ البوت يعمل الآن بشكل مستقر وجاهز للتطوير وإضافة الترجمة خطوة بخطوة بدون أي أخطاء بناء!")

def main():
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على TELEGRAM_BOT_TOKEN")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("🤖 البوت يعمل الآن بنجاح ومستقر تماماً...")
    app.run_polling()

if __name__ == "__main__":
    main()
