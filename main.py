import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# سيرفر وهمي لتلبية شروط رندر وفتح بورت
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك يا فنان! أرسل لي أي مقطع فيديو أو حلقة، وبجهزها لك للترجمة 🎬🚀")

# دالة استقبال الفيديوهات
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        return

    await update.message.reply_text("📥 جاري استقبال الفيديو وتحميله للمعالجة...")
    
    # تحميل الملف المؤقت في السيرفر
    file = await context.bot.get_file(video.file_id)
    downloaded_file_path = "downloaded_video.mp4"
    await file.download_to_drive(downloaded_file_path)
    
    await update.message.reply_text("✅ تم استلام الفيديو بنجاح! جاري التجهيز للترجمة...")
    
    # هنا لاحقاً بنضيف كود التفريغ والترجمة والدمج

async def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على التوكن")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # استقبال أي فيديو أو ملف مرسل
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("البوت يعمل الآن ومستعد لاستقبال الفيديوهات...")
    await app.initialize()
    await app.start()
    app.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    asyncio.run(main())
