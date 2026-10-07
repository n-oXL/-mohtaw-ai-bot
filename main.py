import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

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
    
    # تهيئة بيانات المستخدم المجانية إذا لم تكن موجودة
    if 'free_minutes_left' not in context.user_data:
        context.user_data['free_minutes_left'] = 30.0  # 30 دقيقة مجانية إجمالية
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
            [InlineKeyboardButton("📅 اشتراك أسبوع (15 ريال)", callback_data="pay_week")],
            [InlineKeyboardButton("📅 اشتراك شهر (45 ريال)", callback_data="pay_month")],
            [InlineKeyboardButton("📅 اشتراك ٣ شهور (120 ريال)", callback_data="pay_3months")],
            [InlineKeyboardButton("📅 اشتراك سنة (350 ريال)", callback_data="pay_year")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(
            "💳 **اختر الباقة المناسبة للشراء:**\n\n"
            "بعد اختيار الباقة، ستظهر لك طرق الدفع لإتمام عملية الشراء واستلام كود الاشتراك.",
            reply_markup=InlineKeyboardMarkup(buy_keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("pay_"):
        prices = {
            "pay_week": ("أسبوع", "15 ريال"),
            "pay_month": ("شهر", "45 ريال"),
            "pay_3months": ("٣ شهور", "120 ريال"),
            "pay_year": ("سنة", "350 ريال")
        }
        plan_info = prices.get(data, ("أسبوع", "15 ريال"))
        
        payment_text = (
            f"🛒 **تفاصيل طلب باقة: {plan_info[0]}**\n"
            f"💰 السعر: {plan_info[1]}\n\n"
            "💳 **طرق الدفع المتاحة:**\n"
            "• تحويل بنكي (الراجحي / الإنماء)\n"
            "• STC Pay / Urpay\n\n"
            "يرجى التحويل وإرسال إيصال الدفع للإدارة، وسيتم إرسال كود التفعيل الخاص بك فوراً."
        )
        await query.message.edit_text(
            payment_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="activate_code")],
                [InlineKeyboardButton("🔙 رجوع للباقات", callback_data="buy_subscription")]
            ]),
            parse_mode="Markdown"
        )

    elif data == "activate_code":
        context.user_data['waiting_for_code'] = True
        await query.message.reply_text("🔑 حسناً، يرجى إرسال كود الاشتراك الآن لتفعيله (مثال للتجربة: `WEEK7`):")

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

# 4. معالجة النصوص (إدخال الكود)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_code'):
        code = update.message.text.strip()
        context.user_data['waiting_for_code'] = False
        
        if code in ["WEEK7", "week7", "Faris7"]:
            context.user_data['is_subscribed'] = True
            await update.message.reply_text(
                "✨ تم تفعيل كود الاشتراك بنجاح!\n"
                "لديك الآن دقائق غير محدودة بشروط المحاولات حسب مدة الحلقة.\n"
                "اختر من القائمة قسم الترجمة أو الدبلجة وارسل المقطع لنبدأ الترجمة والدبلجة 🚀",
                reply_markup=get_main_menu_markup()
            )
        else:
            await update.message.reply_text("❌ عذراً، كود الاشتراك غير صحيح. تأكد من الكود أو قم بشراء كود جديد.")
    else:
        await update.message.reply_text("الرجاء استخدام الأزرار في القائمة أو إرسال فيديو للترجمة والدبلجة.")

# 5. معالجة الفيديوهات والتحقق من الشروط والثغرات
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    duration_seconds = getattr(video, 'duration', 60) # افتراضي دقيقة لو ما انقرصت
    duration_minutes = duration_seconds / 60.0

    is_subscribed = context.user_data.get('is_subscribed', False)

    if not is_subscribed:
        # فحص باقة التجربة المجانية (30 دقيقة إجمالية)
        free_left = context.user_data.get('free_minutes_left', 30.0)
        if free_left <= 0:
            await update.message.reply_text(
                "❌ لقد استنفذت الـ 30 دقيقة المجانية الخاصة بك!\n"
                "يرجى شراء كود اشتراك وتفعيله للاستمرار.",
                reply_markup=get_main_menu_markup()
            )
            return
        
        if duration_minutes > free_left:
            await update.message.reply_text(
                f"❌ عذراً، مدة الفيديو ({duration_minutes:.1f} دقيقة) تتجاوز رصيدك المجاني المتبقي ({free_left:.1f} دقيقة).",
                reply_markup=get_main_menu_markup()
            )
            return
        
        # خصم من الباقة المجانية
        context.user_data['free_minutes_left'] = free_left - duration_minutes
    
    else:
        # فحص نظام المحاولات حسب مدة الحلقة للمشتركين
        # (من 25 إلى 60 دقيقة = 3 محاولات / 10 إلى 20 = 5 محاولات / 5 إلى 10 = 10 محاولات / أقل من 5 = 12 محاولة - تتجدد كل 6 ساعات)
        # سيتم تنفيذ حدود المحاولات هنا برمجياً
        pass

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
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("Bot is starting polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
