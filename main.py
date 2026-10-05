import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
# استيراد المكتبات الخاصة بالذكاء الاصطناعي للدبلجة والترجمة
import whisper
from gtts import gTTS

# تحميل نموذج Whisper للتعرف على الكلام وتفريغه
whisper_model = whisper.load_model("base")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التأكد من إرسال مقطع فيديو
    video = update.message.video or update.message.effective_attachment
    if not video:
        return

    await update.message.reply_text("⏳ جاري تحميل الفيديو ومعالجة الصوت بالذكاء الاصطناعي...")

    # 1. تحميل الفيديو المؤقت
    file = await context.bot.get_file(video.file_id)
    input_path = "input_video.mp4"
    output_audio = "extracted_audio.mp3"
    translated_audio = "translated_audio.mp3"
    final_output = "final_output.mp4"

    await file.download_to_drive(input_path)

    try:
        # 2. استخراج الصوت من الفيديو باستخدام FFmpeg
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-q:a", "0", "-map", "a", output_audio],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 3. تفريغ الصوت (Speech-to-Text) باستخدام Whisper
        await update.message.reply_text("🎙️ يتم تفريغ وتدقيق النصوص...")
        result = whisper_model.transcribe(output_audio, task="translate") # task="translate" تترجمه للإنجليزية أو يمكنك ضبطه للعربية مباشرة
        text_content = result.get("text", "")

        # 4. تحويل النص المترجم إلى صوت عربي (Text-to-Speech)
        await update.message.reply_text("🔊 جاري توليد الصوت المدبلج...")
        tts = gTTS(text=text_content, lang='ar', slow=False)
        tts.save(translated_audio)

        # 5. دمج الصوت العربي الجديد مع الفيديو الأصلي وحذف الصوت القديم
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", input_path, "-i", translated_audio,
                "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0",
                "-shortest", final_output
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # 6. إرسال الفيديو النهائي المدبلج للمستخدم
        await update.message.reply_video(video=open(final_output, 'rb'), caption="✨ تم دبلجة المقطع بنجاح!")

    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ أثناء المعالجة التقنية: {str(e)}")

    finally:
        # تنظيف الملفات المؤقتة من السيرفر
        for f in [input_path, output_audio, translated_audio, final_output]:
            if os.path.exists(f):
                os.remove(f)

def main():
    # ضع توكن البوت الخاص بك هنا
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("🤖 البوت يعمل الآن وجاهز لدبلجة الفيديوهات بالذكاء الاصطناعي...")
    app.run_polling()

if __name__ == "__main__":
    main()
