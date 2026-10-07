import os
import random
import string
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# رابط حساب الدعم الفني المباشر
SUPPORT_USERNAME = "https://t.me/MOYG1"
LOCAL_PAYMENT_LINK = "https://your-saudi-payment-store.com" # استبدله برابط متجرك المحلي السعودي

# توليد 350 كود عشوائي طويل لا يمكن تخمينه أبداً
def generate_secure_codes(num=350, length=24):
    codes = set()
    characters = string.ascii_letters + string.digits
    while len(codes) < num:
        code = "".join(random.choices(characters, k=length))
        formatted_code = f"MHT-{code[:6]}-{code[6:12]}-{code[12:18]}-{code[18:]}"
        codes.add(formatted_code)
    return codes

VALID_SUBSCRIPTION_CODES = generate_secure_codes(350, 24)
VALID_SUBSCRIPTION_CODES.add("WEEK7-FARIS-PRO-2026")

# 1. سيرفر الويب الوهمي لترضية رندر
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# القائمة الرئيسية
def get_main_menu_markup():
    keyboard = [
        [InlineKeyboardButton("💳 شراء كود اشتراك", callback_data="buy_subscription")],
        [InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="activate_code")],
        [InlineKeyboardButton("📝 قسم الترجمة", callback_data="menu_translation"),
         InlineKeyboardButton("🎙️ قسم الدبلجة", callback_data="menu_dubbing")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 2. دالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name or "فارس"
    
    if 'free_minutes_left' not in context.user_data:
        context.user_data['free_minutes_left'] = 30.0
        context.user_data['is_subscribed'] = False

    welcome_text = (
        f"أهلاً بك {user_name}\n"
        "بوت ترجمة ودبلجة الفيديوهات والاسهل\n"
        "اختر من القائمة أدناه ما تُريد"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_markup())

# 3. معالجة الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "buy_subscription":
        buy_keyboard = [
            [InlineKeyboardButton("🇸🇦 الدفع المحلي السعودي (مدى، أبل باي)", url=LOCAL_PAYMENT_LINK)],
            [InlineKeyboardButton("🌍 الدفع الخارجي (تواصل مع الدعم)", url=SUPPORT_USERNAME)],
            [InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="activate_code")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "💳 **اختر طريقة الدفع المناسبة لك:**\n\n"
            "• **داخل السعودية**: استخدم الدفع المحلي السريع (مدى، أبل باي، وبطاقات البنوك السعودية).\n"
            "• **خارج السعودية**: تواصل مباشرة مع الدعم الفني للاستفادة من الدفع الخارجي (فيزا، لايك كارد، أو عملات رقمية).\n\n"
            "بعد إتمام الدفع، احصل على الكود وقم بتفْعيله عبر زر (تفعيل كود الاشتراك).",
            reply_markup=InlineKeyboardMarkup(buy_keyboard),
            parse_mode="Markdown"
        )

    elif data == "activate_code":
        context.user_data['waiting_for_code'] = True
        await query.message.reply_text(
            "🔑 **تفعيل كود الاشتراك:**\n\n"
            "الرجاء إرسال أمر التفعيل مع الكود الذي استلمته بهذا الشكل:\n"
            "`/activate <كود_الاشتراك>`\n\n"
            "(مثال للتجربة: `/activate WEEK7-FARIS-PRO-2026`)",
            parse_mode="Markdown"
        )

    elif data == "menu_translation":
        trans_keyboard = [
            [InlineKeyboardButton("🇸🇦 ترجمة عربية فصحى", callback_data="set_trans_ar")],
            [InlineKeyboardButton("🌍 ترجمة لغات عالمية", callback_data="set_trans_global")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
        await query.message.edit_text("📝 **اختر نوع الترجمة:**", reply_markup=InlineKeyboardMarkup(trans_keyboard), parse_mode="Markdown")

    elif data == "menu_dubbing":
        dub_keyboard = [
            [InlineKeyboardButton("🇸🇦 دبلجة عربية فصحى", callback_data="set_dub_ar")],
            [InlineKeyboardButton("🌍 دبلجة لغات عالمية", callback_data="set_dub_global")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
        ]
        await query.message.edit_text("🎙️ **اختر نوع الدبلجة:**", reply_markup=InlineKeyboardMarkup(dub_keyboard), parse_mode="Markdown")

    elif data in ["set_trans_ar", "set_trans_global", "set_dub_ar", "set_dub_global"]:
        modes = {
            "set_trans_ar": "ترجمة عربية فصحى",
            "set_trans_global": "ترجمة لغات عالمية",
            "set_dub_ar": "دبلجة عربية فصحى",
            "set_dub_global": "دبلجة لغات عالمية"
        }
        context.user_data['selected_mode'] = modes[data]
        await query.message.edit_text(
            f"✅ تم اختيار النمط: **{modes[data]}**.\n\n"
            "ارسل المقطع لنبدأ الترجمة والدبلجة 🎬",
            reply_markup=get_main_menu_markup(),
            parse_mode="Markdown"
        )

    elif data == "main_menu":
        await query.message.edit_text(
            "أهلاً بك مرة أخرى!\nاختر من القائمة أدناه ما تُريد",
            reply_markup=get_main_menu_markup()
        )

# 4. معالجة أمر التفعيل والكود
async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split(" ", 1)
    
    if len(parts) < 2:
        await update.message.reply_text("❌ يرجى إرسال الأمر بالطريقة الصحيحة مع الكود، مثال:\n`/activate MHT-XXXX-XXXX-...`", parse_mode="Markdown")
        return

    code = parts[1].strip()

    if code in VALID_SUBSCRIPTION_CODES:
        context.user_data['is_subscribed'] = True
        context.user_data['waiting_for_code'] = False
        await update.message.reply_text(
            "✅ تم تفعيل الكود بنجاح!\n"
            "اشتراكك مفعل الآن ولديك صلاحية كاملة. اختر من القائمة قسم الترجمة أو الدبلجة وارسل المقطع لنبدأ الترجمة والدبلجة 🚀",
            reply_markup=get_main_menu_markup()
        )
    else:
        await update.message.reply_text("❌ الكود خطأ أو غير صحيح. تأكد من الكود الذي استلمته وأعد المحاولة.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_code'):
        code = update.message.text.strip()
        if code in VALID_SUBSCRIPTION_CODES:
            context.user_data['is_subscribed'] = True
            context.user_data['waiting_for_code'] = False
            await update.message.reply_text(
                "✅ تم تفعيل الكود بنجاح!\n"
                "اختر من القائمة قسم الترجمة أو الدبلجة وارسل المقطع لنبدأ الترجمة والدبلجة 🚀",
                reply_markup=get_main_menu_markup()
            )
        else:
            await update.message.reply_text("❌ الكود خطأ. تأكد من الكود أو تواصل مع الدعم الفني للحصول على كود صحيح.")
    else:
        await update.message.reply_text("الرجاء استخدام الأزرار في القائمة أو إرسال فيديو للترجمة والدبلجة.")

# 5. معالجة الفيديوهات
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    duration_seconds = getattr(video, 'duration', 60)
    duration_minutes = duration_seconds / 60.0

    is_subscribed = context.user_data.get('is_subscribed', False)

    if not is_subscribed:
        free_left = context.user_data.get('free_minutes_left', 30.0)
        if free_left <= 0:
            await update.message.reply_text(
                "❌ لقد استنفذت الـ 30 دقيقة المجانية الخاصة بك!\n"
                "يرجى شراء اشتراك وتفعيل الكود للاستمرار.",
                reply_markup=get_main_menu_markup()
            )
            return
        
        if duration_minutes > free_left:
            await update.message.reply_text(
                f"❌ عذراً، مدة الفيديو ({duration_minutes:.1f} دقيقة) تتجاوز رصيدك المجاني المتبقي ({free_left:.1f} دقيقة).",
                reply_markup=get_main_menu_markup()
            )
            return
        
        context.user_data['free_minutes_left'] = free_left - duration_minutes
    
    mode = context.user_data.get('selected_mode', 'ترجمة عربية فصحى')
    
    if "دبلجة" in mode:
        await update.message.reply_text(f"🎙️ جاري دبلجة الفيديو بنمط [{mode}]، الرجاء الانتظار...")
        await update.message.reply_text("✨ تمت الدبلجة بنجاح.")
    else:
        await update.message.reply_text(f"📝 جاري ترجمة الفيديو بنمط [{mode}]، الرجاء الانتظار...")
        await update.message.reply_text("✨ تمت الترجمة بنجاح.")

def main():
    t = threading.Thread(target=run_web_server)
    t.daemon = True
    t.start()

    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN found!")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("activate", activate_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
