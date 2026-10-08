import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ضع توكن البوت الخاص بك هنا
TOKEN = "8722033585:AAGLT35kIiHycgp7jL6-y8trr5ZT2J2OKdo"

# معرف جروب الإدارة (لتلقي التنبيهات)
ADMIN_GROUP_ID = -https://t.me/+cB3crwuCLWI2MzZk

# رابط القناة للشروط ويوزر الدعم الفني
CHANNEL_LINK = "https://t.me/my_translator9"
SUPPORT_USERNAME = "https://t.me/MOYG1"

# إعداد السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# قاموس لتتبع استهلاك المستخدمين في الباقة المجانية (كمثال تجريبي)
# المفتاح: user_id, القيمة: إجمالي الثواني المستخدمة (الحد الأقصى 180 ثانية = 3 دقائق)
free_tier_usage = {}


# أمر البداية /start والقائمة الرئيسية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [InlineKeyboardButton("🎙️ قسم الدبلجة", callback_data="dubbing_menu")],
      [InlineKeyboardButton("📝 قسم الترجمة", callback_data="translation_menu")],
      [InlineKeyboardButton("💳 شراء كود اشتراك", callback_data="buy_code_menu")],
      [
          InlineKeyboardButton(
              "🔑 تفعيل كود الاشتراك", callback_data="activate_code_menu"
          )
      ],
      [InlineKeyboardButton("📊 اشتراكي", callback_data="my_subscription")],
      [InlineKeyboardButton("🎧 قسم الدعم الفني", url=SUPPORT_USERNAME)],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_text = "أهلاً بك في بوت مترجمي\nاختر القسم المناسب للبدء في الخدمة:"

  if update.callback_query:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(welcome_text, reply_markup=reply_markup)
  else:
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


# قائمة قسم الدبلجة
async def dubbing_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  keyboard = [
      [
          InlineKeyboardButton(
              "دبلجة عربية فصحى", callback_data="dub_arabic_classic"
          )
      ],
      [
          InlineKeyboardButton(
              "دبلجة لُغات العالم", callback_data="dub_world_languages"
          )
      ],
      [
          InlineKeyboardButton(
              "🔙 رجوع للقائمة الرئيسية", callback_data="main_menu"
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  await query.message.edit_text(
      "🎙️ اختر نوع الدبلجة المطلوبة:", reply_markup=reply_markup
  )


# قائمة قسم الترجمة
async def translation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  keyboard = [
      [
          InlineKeyboardButton(
              "ترجمة عربية فصحى", callback_data="trans_arabic_classic"
          )
      ],
      [
          InlineKeyboardButton(
              "ترجمة لُغات العالم", callback_data="trans_world_languages"
          )
      ],
      [
          InlineKeyboardButton(
              "🔙 رجوع للقائمة الرئيسية", callback_data="main_menu"
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  await query.message.edit_text(
      "📝 اختر نوع الترجمة المطلوبة:", reply_markup=reply_markup
  )


# قسم شراء كود اشتراك
async def buy_code_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  keyboard = [
      [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  buy_text = (
      "💳 **شراء كود اشتراك:**\n\n"
      "لشراء اشتراك جديد، يرجى التواصل مباشرة مع الدعم الفني لتأكيد الدفع واستلام"
      " الكود الخاص بك."
  )
  await query.message.edit_text(
      buy_text, reply_markup=reply_markup, parse_mode="Markdown"
  )


# قسم تفعيل كود الاشتراك
async def activate_code_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  keyboard = [
      [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  activate_text = (
      "🔑 **تفعيل كود الاشتراك:**\n\n"
      "الرجاء إرسال أمر التفعيل مع الكود الذي استلمته بهذا الشكل:\n"
      "`/activate <كود_الاشتراك>`\n\n"
      "(مثال للتجربة: `/activate WEEK7-FARIS-PRO-2026`)"
  )
  await query.message.edit_text(
      activate_text, reply_markup=reply_markup, parse_mode="Markdown"
  )


# قسم عرض تفاصيل اشتراك المستخدم
async def my_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  keyboard = [
      [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  sub_text = (
      "📊 **معلومات اشتراكك:**\n\n"
      "• نوع الباقة: **المجانية**\n"
      "• الرصيد المتبقي: مخصص لإجمالي 3 دقائق (تراكمي للمقاطع)\n"
      "• اللغات المتاحة: (هندي، هولندي، إسباني، بريطاني)\n\n"
      "💡 *الباقات المدفوعة تتيح لك 10 مقاطع باليوم، لغات كثيرة جداً، ونظام"
      " المحاولات حسب مدة المقطع:* \n"
      " - من 35 إلى 60 دقيقة: محاولة واحدة\n"
      " - من 20 إلى 35 دقيقة: محاولتان\n"
      " - من 10 إلى 20 دقيقة: ثلاث محاولات\n"
      " - من 0.01 إلى 10 دقائق: خمس محاولات"
  )
  await query.message.edit_text(
      sub_text, reply_markup=reply_markup, parse_mode="Markdown"
  )


# التعامل مع اختيار خيار دبلجة أو ترجمة وإرسال رسالة مستقلة جديدة
async def handle_sub_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  data = query.data

  if "dub_" in data:
    response_msg = (
        "تم اختيار قسم الدبلجة.\n"
        "أهلاً بك في قسم الدبلجة، ارسل المقطع لنبدأ ترجمته.\n\n"
        f"📌 تأكد أن المقطع يتوافق مع شروط البوت: {CHANNEL_LINK}"
    )
  elif "trans_" in data:
    response_msg = (
        "تم اختيار قسم الترجمة.\n"
        "أهلاً بك في قسم الترجمة، ارسل المقطع لنبدأ ترجمته.\n\n"
        f"📌 تأكد أن المقطع يتوافق مع شروط البوت: {CHANNEL_LINK}"
    )
  else:
    return

  await context.bot.send_message(
      chat_id=query.message.chat_id, text=response_msg
  )


# أمر تفعيل الكود
async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not context.args:
    await update.message.reply_text(
        "❌ الصيغة غير صحيحة.\nالرجاء الاستخدام بهذا الشكل:\n`/activate"
        " <كود_الاشتراك>`",
        parse_mode="Markdown",
    )
    return

  code = context.args[0]
  await update.message.reply_text(
      f"⏳ جاري التحقق من الكود: `{code}` وتفعيل الاشتراك...", parse_mode="Markdown"
  )


# فحص الملفات والمقاطع الواردة وتنبيه الإدارة أو خصم رصيد الباقة المجانية
async def handle_incoming_media(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  user = update.message.from_user
  user_id = user.id

  # افترضنا أن مدة المقطع المرسل بالثواني (مثلاً نجلب مدة الفيديو الفعلية هنا)
  # للتوضيح سنفترض أن المقطع مدته 30 ثانية كمثال:
  video_duration_seconds = 30

  # التحقق من رصيد الباقة المجانية التراكمي (3 دقائق = 180 ثانية)
  current_usage = free_tier_usage.get(user_id, 0)
  max_free_seconds = 180  # 3 دقائق

  if current_usage >= max_free_seconds:
    # رسالة انتهاء الاشتراك المجاني مع العرض
    expired_msg = (
        "بما أن انتهى اشتراكك أتمنى أعجبتك الباقة ونالت حُسن رضاك، نقدم لك خصماً"
        " على باقة الأسبوع من 15 ريال إلى 10 ريال، وينتهي العرض بعد يومين."
    )
    await update.message.reply_text(expired_msg)
    return

  # تحديث الاستهلاك التراكمي للمستخدم
  free_tier_usage[user_id] = current_usage + video_duration_seconds

  is_spam_or_violation = False  # ضع شرط فحص السبام أو المحتوى المخالف هنا

  if is_spam_or_violation:
    alert_text = (
        f"⚠️ **تنبيه مخالفة / سبام جديد!**\n"
        f"👤 المستخدم: {user.full_name} (@{user.username or 'لا يوجد'})\n"
        f"🆔 الآيدي: `{user.id}`\n"
        f"📌 تم رصد محتوى مشبوه (إباحي/عنف/سبام) ويتطلب تدخلك للحظر اليدوي."
    )
    await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID, text=alert_text, parse_mode="Markdown"
    )
    await update.message.reply_text(
        "عذراً، تم رصد مخالفة في المحتوى المرسل وتم إبلاغ الإدارة."
    )
  else:
    await update.message.reply_text(
        "✅ تم استلام المقطع بنجاح، جاري معالجته..."
    )


def main():
  app = ApplicationBuilder().token(TOKEN).build()

  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler("activate", activate_command))
  app.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
  app.add_handler(CallbackQueryHandler(dubbing_menu, pattern="^dubbing_menu$"))
  app.add_handler(
      CallbackQueryHandler(translation_menu, pattern="^translation_menu$")
  )
  app.add_handler(
      CallbackQueryHandler(buy_code_menu, pattern="^buy_code_menu$")
  )
  app.add_handler(
      CallbackQueryHandler(activate_code_menu, pattern="^activate_code_menu$")
  )
  app.add_handler(
      CallbackQueryHandler(my_subscription, pattern="^my_subscription$")
  )
  app.add_handler(
      CallbackQueryHandler(
          handle_sub_category,
          pattern="^(dub_arabic_classic|dub_world_languages|trans_arabic_classic|trans_world_languages)$",
      )
  )

  app.add_handler(
      MessageHandler(
          filters.VIDEO | filters.AUDIO | filters.Document.ALL,
          handle_incoming_media,
      )
  )

  print("Bot is running...")
  app.run_polling()


if __name__ == "__main__":
  main()
