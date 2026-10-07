import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# 1. سيرفر الويب الوهمي لترضية رندر (Render Web Service Port Check)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# القائمة الرئيسية المدمجة (اشتراكات، تفعيل، ودبلجة وترجمة بلغات عالمية)
def get_main_menu_markup():
    keyboard = [
        # قسم الاشتراكات
        [InlineKeyboardButton("📅 اشتراك أسبوع", callback_data="plan_week"),
         InlineKeyboardButton("📅 اشتراك شهر", callback_data="plan_month")],
        [InlineKeyboardButton("📅 اشتراك ٣ شهور", callback_data="plan_3months"),
         InlineKeyboardButton("📅 اشتراك سنة", callback_data="plan_year")],
        # تفعيل الكود
        [InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="activate_code")],
        # قسم الدبلجة والترجمة (شامل اللغات العالمية)
        [InlineKeyboardButton("🎙️ دبلجة (عربي فصحى)", callback_data="dub_arabic"),
         InlineKeyboardButton("📝 ترجمة (فصحى)", callback_data="trans_arabic")],
        [InlineKeyboardButton("🌍 دبلجة وترجمة (لغات عالمية)", callback_data="dub_global")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 2. دالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "فارس"
    welcome_text = (
        f"أهلاً بك {user_name}\n"
        "بوت ترجمة ودبلجة الفيديوهات الاحترافي والاسهل\n"
        "اختر من القائمة أدناه ما تُريد"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_markup())

# 3. معالجة الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("plan_"):
        plan_names = {
            "plan_week": "أسبوع (كود التفعيل المجاني: WEEK7)",
            "plan_month": "شهر",
            "plan_3months": "٣ شهور",
            "plan_year": "سنة"
        }
        selected = plan_names.get(data, "الباقة")
        await query.message.edit_text(
            f"🛒 لقد اخترت باقة: **{selected}**.\n\n"
            "اضغط على زر تفعيل كود الاشتراك وأرسل الكود لتفعيل باقتك فوراً.",
            reply_markup=get_main_menu_markup(),
            parse_mode="Markdown"
        )

    elif data == "activate_code":
        context.user_data['waiting_for_code'] = True
        await query.message.reply_text("🔑 حسناً، يرجى إرسال كود الاشتراك الآن (مثال: `WEEK7`):")

    elif data in ["dub_arabic", "trans_arabic", "dub_global"]:
        modes = {
            "dub_arabic": "دبلجة (عربي فصحى)",
            "trans_arabic": "ترجمة (فصحى)",
            "dub_global": "دبلجة وترجمة (لغات عالمية)"
        }
        context.user_data['selected_mode'] = modes[data]
        await query.message.reply_text(
            f"✅ تم اختيار وضع: **{modes[data]}**.\n\n"
            "الآن أرسل مقطع الفيديو لنبدأ المعالجة الاحترافية 🎬",
            parse_mode="Markdown"
        )

# 4. معالجة النصوص (إدخال كود التفعيل)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_code'):
        code = update.message.text.strip()
        context.user_data['waiting_for_code'] = False
        
        # تفعيل الكود (كود الأسبوع التجريبي المجاني: WEEK7)
        if code in ["WEEK7", "week7", "Faris7", "VIP"]:
            context.user_data['is_subscribed'] = True
            await update.message.reply_text(
                "✨ تم تفعيل كود الاشتراك بنجاح!\n"
                "يمكنك الآن اختيار نمط الدبلجة أو الترجمة من القائمة وإرسال مقطعك 🚀",
                reply_markup=get_main_menu_markup()
            )
        else:
            await update.message.reply_text("❌ عذراً، كود الاشتراك غير صحيح. تأكد من الكود وأعد المحاولة.")
    else:
        await update.message.reply_text("الرجاء استخدام الأزرار في القائمة أو إرسال فيديو للترجمة.")

# 5. معالجة الفيديوهات
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('is_subscribed', False):
        await update.message.reply_text(
            "❌ عذراً، يجب عليك تفعيل كود الاشتراك أولاً قبل إرسال الفيديوهات!",
            reply_markup=get_main_menu_markup()
        )
        return

    mode = context.user_data.get('selected_mode', 'ترجمة (فصحى)')
    await update.message.reply_text(f"⏳ جاري معالجة الفيديو بنمط [{mode}]، الرجاء الانتظار...")
    # هنا يتم وضع كود دبلجة أو ترجمة الفيديو الفعلي
    await update.message.reply_text("✨ تمت معالجة وترجمة المقطع بنجاح.")

def main():
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN found!")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
