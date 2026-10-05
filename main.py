import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

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

# دالة البداية مع أزرار اختيار لغة الدردشة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="ui_ar"),
            InlineKeyboardButton("🇬🇧 English", callback_data="ui_en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك في بوت مُترجمي 🎬🚀\n"
        "Welcome to My Translator Bot!\n\n"
        "الرجاء اختيار لغة العرض المفضلة لديك:\n"
        "Please choose your preferred language:",
        reply_markup=reply_markup
    )

# دالة استقبال الفيديوهات وعرض قائمة خيارات الترجمة
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        return

    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية (فصحى)", callback_data="lang_ar_formal"),
            InlineKeyboardButton("😎 العربية (عامية)", callback_data="lang_ar_slang")
        ],
        [
            InlineKeyboardButton("🇬🇧 الإنجليزية (English)", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📥 تم استلام الفيديو بنجاح!\nاختر لغة الترجمة المستهدفة:",
        reply_markup=reply_markup
    )

# دالة التعامل مع جميع الأزرار التفاعلية
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    # تفاعلات اختيار لغة الواجهة عند البدء مع شروط المقاطع
    if choice == "ui_ar":
        await query.edit_message_text(
            "✅ تم اختيار اللغة العربية.\n\n"
            "🎬 **أرسل لي المقطع الآن وفقاً للشروط التالية لضمان نجاح المعالجة:**\n"
            "• **الصيغ المدعومة:** MP4, MOV, MKV\n"
            "• **المدة المقبولة:** أقصى مدة يفضل أن تكون ضمن المعقول (أقل من 15-20 دقيقة للحلقة)\n"
            "• **الحجم الأقصى:** يفضل ألا يتجاوز حجم الملف الحدود المسموحة لضمان السرعة وعدم توقف السيرفر.\n\n"
            "بانتظار مقطعك يا فنان!"
        )
    elif choice == "ui_en":
        await query.edit_message_text(
            "✅ English has been selected.\n\n"
            "🎬 **Please send your video clip according to the following guidelines:**\n"
            "• **Supported Formats:** MP4, MOV, MKV\n"
            "• **Duration:** Best kept under reasonable limits (e.g., under 15-20 mins per episode)\n"
            "• **Max Size:** Keep file size reasonable to avoid server timeouts.\n\n"
            "Waiting for your clip!"
        )
    
    # تفاعلات اختيار لغة الترجمة للفيديو
    elif choice == "lang_ar_formal":
        await query.edit_message_text("✅ تم اختيار: الترجمة إلى العربية (فصحى).\n⏳ جاري بدء المعالجة والترجمة...")
    elif choice == "lang_ar_slang":
        await query.edit_message_text("✅ تم اختيار: الترجمة إلى العربية (عامية).\n⏳ جاري بدء المعالجة والترجمة...")
    elif choice == "lang_en":
        await query.edit_message_text("✅ تم اختيار: الترجمة إلى الإنجليزية.\n⏳ جاري بدء المعالجة والترجمة...")

async def main():
    if not TOKEN:
        print("خطأ: لم يتم العثور على التوكن")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("البوت يعمل الآن...")
    await app.initialize()
    await app.start()
    app.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    asyncio.run(main())
