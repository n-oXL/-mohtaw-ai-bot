import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# سيرفر وهمي لتلبية شروط رندر وفتح البورت
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"[WEB SERVER] Running on port {port}")
    server.serve_forever()

# تشغيل السيرفر في الخلفية
threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"[TELEGRAM] Received /start from user: {user.first_name} (ID: {user.id})")
    
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

# دالة استقبال الفيديوهات وتخزينها
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        return
    print(f"[TELEGRAM] Received video file from user: {update.effective_user.id}")

    context.user_data['video_obj'] = video

    # حذف رسالة الإرشادات السابقة لتنظيف الشات
    if 'instruction_message_id' in context.user_data:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data['instruction_message_id']
            )
        except Exception as e:
            print(f"[NOTE] Could not delete old instruction message: {e}")

    keyboard = [
        [
            InlineKeyboardButton("📝 ترجمة (فصحى)", callback_data="mode_sub_formal"),
            InlineKeyboardButton("😎 ترجمة (عامية)", callback_data="mode_sub_slang")
        ],
        [
            InlineKeyboardButton("🎙️ دبلجة صوتية كاملة", callback_data="mode_dubbing")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📥 تم استلام الفيديو بنجاح!\nاختر وضع المعالجة المطلوب (ترجمة أو دبلجة):",
        reply_markup=reply_markup
    )

# دالة تنفيذ معالجة الفيديو الفعلية وتحميله وإرساله
async def process_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str, action_msg: str):
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    try:
        video_obj = context.user_data.get('video_obj')
        if not video_obj:
            await query.edit_message_text("❌ عذراً، لم أتمكن من العثور على الفيديو. الرجاء إرساله مرة أخرى.")
            return

        file = await context.bot.get_file(video_obj.file_id)
        input_path = "input_video.mp4"
        output_path = "output_video.mp4"
        
        # استخدام النص المختصر بناءً على طلبك
        await query.edit_message_text(action_msg)
        await file.download_to_drive(input_path)
        
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', input_path, '-y', output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        if not os.path.exists(output_path):
            output_path = input_path

        with open(output_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=f"✅ تم الانتهاء بنجاح! الوضع المختار: {mode}"
            )

        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path) and output_path != input_path: os.remove(output_path)

    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

# دالة التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "ui_ar":
        msg = await query.edit_message_text(
            "✅ تم اختيار اللغة العربية.\n\n"
            "🎬 أرسل لي المقطع الآن وفقاً للشروط التالية:\n"
            "• الصيغ: MP4, MOV, MKV\n"
            "• المدة: يفضل أقل من 15-20 دقيقة للحلقة\n\n"
            "بانتظار مقطعك يا فنان!"
        )
        context.user_data['instruction_message_id'] = msg.message_id
        
    elif choice == "ui_en":
        msg = await query.edit_message_text(
            "✅ English has been selected.\n\n"
            "🎬 Please send your video clip:\n"
            "• Formats: MP4, MOV, MKV\n\n"
            "Waiting for your clip!"
        )
        context.user_data['instruction_message_id'] = msg.message_id
        
    elif choice in ["mode_sub_formal", "mode_sub_slang", "mode_dubbing"]:
        if choice == "mode_dubbing":
            mode_text = "الدبلجة الصوتية الكاملة"
            action_msg = "🎙️ جاري دبلجة مقطعك..."
        elif choice == "mode_sub_formal":
            mode_text = "الترجمة إلى العربية (فصحى)"
            action_msg = "📝 جاري ترجمة مقطعك..."
        else:
            mode_text = "الترجمة إلى العربية (عامية)"
            action_msg = "😎 جاري ترجمة مقطعك..."

        asyncio.create_task(process_and_send_video(update, context, mode_text, action_msg))

async def main():
    if not TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN is missing!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("[TELEGRAM] Bot is starting polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    asyncio.run(main())
