import os
import subprocess
import whisper
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("⏳ جاري تحميل نموذج الذكاء الاصطناعي...")
model = whisper.load_model("base")
print("✅ تم تحميل النموذج بنجاح، البوت جاهز!")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    video = message.video or message.document or message.audio
    if not video:
        await message.reply_text("الرجاء إرسال فيديو صحيح.")
        return

    await message.reply_text("📥 جاري تحميل الفيديو ومعالجته، انتظر قليلاً...")

    file = await context.bot.get_file(video.file_id)
    input_video_path = "input_video.mp4"
    output_video_path = "output_video.mp4"
    srt_path = "subtitles.srt"
    
    await file.download_to_drive(input_video_path)

    await message.reply_text("🎙️ جاري تفريغ الصوت وترجمته...")

    result = model.transcribe(input_video_path, task="translate")
    
    segments = result["segments"]
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            start = format_time(segment["start"])
            end = format_time(segment["end"])
            text = segment["text"].strip()
            srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    await message.reply_text("🎬 جاري دمج الترجمة على الفيديو...")

    ffmpeg_cmd = (
        f"ffmpeg -y -i {input_video_path} -vf \"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&H00FFFF&'\" "
        f"-c:a copy {output_video_path}"
    )
    
    subprocess.run(ffmpeg_cmd, shell=True, capture_output=True)

    if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
        await message.reply_video(video=open(output_video_path, 'rb'), caption="✨ تفضل الفيديو مع الترجمة الكاملة!")
    else:
        await message.reply_text("⚠️ حدث خطأ أثناء دمج الترجمة على الفيديو.")

    for path in [input_video_path, output_video_path, srt_path]:
        if os.path.exists(path):
            os.remove(path)

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def main():
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على TELEGRAM_BOT_TOKEN")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("🤖 البوت يعمل الآن ويستمع للفيديوهات...")
    app.run_polling()

if __name__ == "__main__":
    main()
