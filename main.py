import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# إعداد السجلات (Logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# قاعدة بيانات وهمية مؤقتة (تستبدل لاحقاً بقاعدة بيانات حقيقية مثل SQLite أو PostgreSQL)
users_db = {}

# إعدادات النظام والشروط الصارمة لحماية الـ API والسيرفر
MAX_TRIAL_CLIPS = 3          # عدد المقاطع التجريبية المجانية لكل مستخدم
MAX_TRIAL_DURATION = 10      # أقصى حد لطول المقطع المجاني الواحد (10 دقائق) لمنع حرق الـ API بحلقات المسلسلات
MAX_PAID_DURATION = 60       # أقصى حد لطول المقطع في الباقات المدفوعة (60 دقيقة)

# 1. أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # منح باقة التجربة المجانية للمستخدم الجديد (مربوطة بالـ Telegram ID وبعدد المقاطع)
    if user_id not in users_db:
        users_db[user_id] = {
            "status": "trial",
            "clips_left": MAX_TRIAL_CLIPS,
            "tier": "التجربة المجانية"
        }

    welcome_text = (
        f"👋 أهلاً بك يا غالي!\n\n"
        "أنا بوت ترجمة ودبلجة الفيديوهات الاحترافي.\n"
        "أرسل لي أي مقطع فيديو وسأقوم بمعالجته فوراً بدقة عالية.\n\n"
        "اختر من القائمة أدناه أو أرسل الفيديو للبدء 👇"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 اشتراكي", callback_data="my_subscription")],
        [InlineKeyboardButton("🔑 تفعيل كود الاشتراك", callback_data="activate_help")]
    ])

    await update.message.reply_text(welcome_text, reply_markup=keyboard)


# 2. عرض قائمة "اشتراكي"
async def subscription_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    user_data = users_db.get(user_id, {"status": "trial", "clips_left": MAX_TRIAL_CLIPS, "tier": "تجريبي"})
    
    status_text = "🟢 فعال" if user_data["clips_left"] > 0 or user_data["status"] == "active" else "🔴 منتهي"

    text = (
        f"📊 تفاصيل اشتراكي:\n\n"
        f"• نوع الباقة: {user_data['tier']}\n"
        f"• حالة الاشتراك: {status_text}\n"
        f"• المقاطع المتاحة لديك: {user_data['clips_left']} مقاطع\n\n"
        f"لترقية باقتك، يرجى شحن كود التفعيل عبر الأمر:\n`/activate [الكود]`"
    )
    
    await query.message.edit_text(text, parse_mode="Markdown")


# 3. تفعيل كود الاشتراك عبر الأمر /activate
async def activate_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text("⚠️ يرجى كتابة الكود بعد الأمر هكذا:\n`/activate VIP-XXXX`", parse_mode="Markdown")
        return

    code = args[0]
    
    # التحقق من كود التفعيل (يرتبط بمتجرك لاحقاً)
    if code.startswith("VIP-"): 
        users_db[user_id] = {
            "status": "active",
            "clips_left": 999, # رصيد غير محدود بذكاء للباقة المدفوعة
            "tier": "الباقة المدفوعة الاحترافية"
        }
        await update.message.reply_text("✨ تم تفعيل باقتك المدفوعة بنجاح! استمتع بخدمات غير محدودة.")
    else:
        await update.message.reply_text("❌ عذراً، كود التفعيل غير صحيح أو منتهي الصلاحية.")


# 4. استقبال الفيديو مع فحص الثغرات وطول المقطع
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # التحقق من رصيد المستخدم
    user_data = users_db.get(user_id, {"clips_left": 0, "status": "trial"})
    if user_data["clips_left"] <= 0:
        await update.message.reply_text(
            "⚠️ عذراً، انتهت مقاطعك المجانية!\n"
            "للاشتراك وشحن رصيدك، يرجى زيارة المتجر وتفعيل الكود عبر الأمر `/activate`."
        )
        return

    # فحص طول الفيديو لمنع استغلال التجربة المجانية بحلقات المسلسلات
    video = update.message.video
    if video:
        video_duration_minutes = video.duration / 60
        
        # قفل التجربة المجانية بمقاطع أقصاها 10 دقائق
        if user_data["status"] == "trial" and video_duration_minutes > MAX_TRIAL_DURATION:
            await update.message.reply_text(
                f"⚠️ عذراً، أقصى طول مسموح للمقطع في **التجربة المجانية** هو {MAX_TRIAL_DURATION} دقائق فقط!\n"
                "لرفع مقاطع طويلة وحلقات مسلسلات، يرجى ترقية حسابك إلى الباقة المدفوعة عبر الأمر `/activate`."
            )
            return
            
        # فحص مقاطع الباقات المدفوعة (أقصى حد 60 دقيقة)
        if user_data["status"] == "active" and video_duration_minutes > MAX_PAID_DURATION:
            await update.message.reply_text(
                f"⚠️ عذراً، الحد الأقصى لطول المقطع الواحد هو {MAX_PAID_DURATION} دقيقة."
            )
            return

    # واجهة الخيارات النظيفة
    prompt_text = "⚙️ كيف ترغب في معالجة هذا الفيديو؟"
    
    options_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 ترجمة (فصحى)", callback_data="trans_formal"),
            InlineKeyboardButton("🎙️ دبلجة (عربي فصحى)", callback_data="dub_ar_formal")
        ],
        [
            InlineKeyboardButton("🌍 دبلجة (لغات عالمية)", callback_data="dub_global_lang")
        ]
    ])

    await update.message.reply_text(prompt_text, reply_markup=options_markup)


# 5. معالجة اختيار لغات الدبلجة العالمية
async def handle_dub_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    languages_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇪🇸 إسباني", callback_data="lang_es"),
            InlineKeyboardButton("🇮🇳 هندي", callback_data="lang_hi")
        ],
        [
            InlineKeyboardButton("🇳🇱 هولندي", callback_data="lang_nl"),
            InlineKeyboardButton("🇬🇧 إنجليزي", callback_data="lang_en")
        ],
        [
            InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")
        ]
    ])

    await query.message.edit_text("🌍 اختر لغة الدبلجة المستهدفة:", reply_markup=languages_markup)


# 6. بدء المعالجة الفعلية للمقطع
async def process_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # خصم مقطع من رصيد المستخدم التجريبي فقط
    if user_id in users_db and users_db[user_id]["status"] == "trial":
        users_db[user_id]["clips_left"] -= 1

    # رسائل النظام النظيفة
    await query.message.edit_text("⏳ جاري الترجمة، الرجاء الانتظار...")
    
    # [هنا يوضع كود ربط الذكاء الاصطناعي والـ API مستقبلاً]
    
    # بعد اكتمال المعالجة:
    await query.message.reply_text("✨ تمت ترجمة المقطع.")


def main():
    # سحب التوكن أوتوماتيكياً من متغيرات البيئة في رندر (BOT_TOKEN)
    TOKEN = os.environ.get("BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("❌ خطأ: لم يتم العثور على متغير البيئة BOT_TOKEN!")

    app = ApplicationBuilder().token(TOKEN).build()

    # الأوامر الأساسية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("activate", activate_code))
    
    # استقبال الفيديوهات
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    
    # معالجة الضغط على الأزرار
    app.add_handler(CallbackQueryHandler(subscription_menu, pattern="my_subscription"))
    app.add_handler(CallbackQueryHandler(handle_dub_languages, pattern="dub_global_lang"))
    app.add_handler(CallbackQueryHandler(process_action, pattern="^(trans_|dub_ar_formal|lang_)"))

    print("🤖 البوت يعمل الآن وجاهز...")
    app.run_polling()

if __name__ == "__main__":
    main()
