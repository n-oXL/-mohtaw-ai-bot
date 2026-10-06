import os
import asyncio
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI

# إعداد السيرفر المحلي لضمان استقرار البوت على الاستضافات
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# دالة ذكية لتحميل خط Cairo أوتوماتيكياً لو لم يكن موجوداً
def ensure_font_exists():
    font_path = "Cairo-Regular.ttf"
    if not os.path.exists(font_path):
        print("[INFO] Downloading Cairo font automatically...")
        try:
            # رابط مباشر لتحميل خط Cairo بصيغة ttf من مصدر موثوق
            font_url = "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Regular.ttf"
            urllib.request.urlretrieve(font_url, font_path)
            print("[INFO] Font downloaded successfully!")
        except Exception as e:
            print(f"[WARNING] Could not download font automatically: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data="ui_ar"),
            InlineKeyboardButton("🇬🇧 English", callback_data="ui_en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك في بوت مُترجمي السينمائي 🎬🚀\nالرجاء اختيار لغة العرض المفضلة لديك:",
        reply_markup=reply_markup
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    if not video:
        return

    context.user_data['video_obj'] = video

    keyboard = [
        [
            InlineKeyboardButton("📝 ترجمة أفلام (فصحى)", callback_data="mode_sub_formal"),
            InlineKeyboardButton("😎 ترجمة أفلام (عامية)", callback_data="mode_sub_slang")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📥 تم استلام الفيديو بنجاح!\nاختر نمط الترجمة المطلوب:",
        reply_markup=reply_markup
    )

async def process_and_send_subtitle(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str, action_msg: str):
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    input_path = "input_video.mp4"
    audio_path = "extracted_audio.mp3"
    output_path = "output_video.mp4"
    font_path = "Cairo-Regular.ttf"
    
    # التأكد من توفر الخط قبل بدء المعالجة
    ensure_font_exists()
    
    try:
        video_obj = context.user_data.get('video_obj')
        if not video_obj:
            await query.edit_message_text("❌ عذراً، لم أتمكن من العثور على الفيديو.")
            return

        file = await context.bot.get_file(video_obj.file_id)
        await query.edit_message_text(action_msg)
        
        # 1. تحميل الفيديو الأصلي
        await file.download_to_drive(input_path)

        # 2. استخراج الصوت من الفيديو باستخدام FFmpeg
        extract_process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-y', '-i', input_path, '-vn', '-acodec', 'libmp3lame', '-q:a', '4', audio_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await extract_process.communicate()

        # 3. إرسال الصوت لـ OpenAI Whisper API حصرياً
        transcribed_text = ""
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            with open(audio_path, "rb") as audio_file:
                prompt_instruction = "Translate and transcribe accurately into cinematic Arabic subtitles." if mode == "فصحى" else "Translate accurately into casual cinematic Arabic slang."
                
                try:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        prompt=prompt_instruction
                    )
                    transcribed_text = transcript.text
                except Exception as api_err:
                    print(f"[OPENAI API ERROR]: {api_err}")
                    transcribed_text = f"خطأ API: {str(api_err)}"

        if not transcribed_text:
            transcribed_text = "لم يتم رصد صوت واضح في المقطع"

        # تنظيف النص لمنع أخطاء الـ FFmpeg
        clean_text = transcribed_text.replace("'", "").replace('"', "").replace("\n", " ")
        if len(clean_text) > 80:
            clean_text = clean_text[:77] + "..."

        # تجهيز فلتر الرسم مع استخدام الخط المحمل أوتوماتيكياً
        if os.path.exists(font_path):
            vf_filter = f"drawtext=fontfile='{font_path}':text='{clean_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.7:boxborderw=6:x=(w-text_w)/2:y=h-th-50"
        else:
            vf_filter = f"drawtext=text='{clean_text}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.7:boxborderw=6:x=(w-text_w)/2:y=h-th-50"

        # 4. دمج الترجمة بالفيديو
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-y', '-i', input_path, 
            '-vf', vf_filter, 
            '-c:v', 'libx264', '-preset', 'ultrafast', 
            '-c:a', 'copy', 
            output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            output_path = input_path
            print(f"[FFmpeg Error]: {stderr.decode('utf-8', errors='ignore')}")

        # 5. إرسال الفيديو للمستخدم
        with open(output_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=f"✨ تمت المعالجة وحرق الترجمة عبر Whisper ({mode})"
            )

    except Exception as e:
        print(f"[ERROR] {e}")
        await query.edit_message_text(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

    finally:
        for p in [input_path, audio_path, output_path]:
            if os.path.exists(p) and p != output_path:
                try: os.remove(p)
                except: pass

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    
    if choice == "ui_ar":
        await query.edit_message_text("✅ تم اختيار العربية. أرسل مقطع الفيديو الآن:")
    elif choice == "ui_en":
        await query.edit_message_text("✅ English selected. Send your video clip now:")
    elif choice in ["mode_sub_formal", "mode_sub_slang"]:
        mode_names = {
            "mode_sub_formal": ("فصحى", "🎙️ جاري استخراج الصوت وتفريغه عبر Whisper (فصحى)..."),
            "mode_sub_slang": ("عامية", "🎙️ جاري استخراج الصوت وتفريغه عبر Whisper (عامية)...")
        }
        mode_text, action_msg = mode_names[choice]
        asyncio.create_task(process_and_send_subtitle(update, context, mode_text, action_msg))

async def main():
    if not TOKEN:
        return
    # تحميل الخط عند تشغيل البوت لأول مرة
    ensure_font_exists()
    
    app = ApplicationBuilder().token(TOKEN).read_timeout(60).write_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
