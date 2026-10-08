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

TOKEN = "8722033585:AAGLT35kIiHycgp7jL6-y8trr5ZT2J20Kdo"
ADMIN_GROUP_ID = -1005398355811
CHANNEL_LINK = "https://t.me/my_translator9"
SUPPORT_USERNAME = "https://t.me/MOYG1"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

free_tier_usage = {}
user_subscriptions = {}


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
      [InlineKeyboardButton("قسم الدعم الفني", url=SUPPORT_USERNAME)],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  welcome_text = "أهلاً بك في بوت مترجمي\nاختر القسم المناسب للبدء في الخدمة:"

  if update.callback_query:
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(welcome_text, reply_markup=reply_markup)
  else:
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


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
              "دبلجة لُغات العالم", callback_data="dub_world_languages_list"
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
              "ترجمة لُغات العالم", callback_data="trans_world_languages_list"
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


async def dub_world_languages_list(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  query = update.callback_query
  await query.answer()
  keyboard = [
      [
          InlineKeyboardButton("🇬🇧 الإنجليزية", callback_data="lang_dub_en"),
          InlineKeyboardButton("🇫🇷 الفرنسية", callback_data="lang_dub_fr"),
      ],
      [
          InlineKeyboardButton("🇪🇸 الإسبانية", callback_data="lang_dub_es"),
          InlineKeyboardButton("🇩🇪 الألمانية", callback_data="lang_dub_de"),
      ],
      [
          InlineKeyboardButton("🇮🇹 الإيطالية", callback_data="lang_dub_it"),
          InlineKeyboardButton("🇹🇷 التركية", callback_data="lang_dub_tr"),
      ],
      [
          InlineKeyboardButton("🇮🇳 الهندية", callback_data="lang_dub_hi"),
          InlineKeyboardButton("🇳🇱 الهولندية", callback_data="lang_dub_nl"),
      ],
      [
          InlineKeyboardButton(
              "🔙 رجوع لقسم الدبلجة", callback_data="dubbing_menu"
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await query.message.edit_text(
      "🌍 اختر اللغة المستهدفة لدبلجة لغات العالم:", reply_markup=reply_markup
  )


async def trans_world_languages_list(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  query = update.callback_query
  await query.answer()
  keyboard = [
      [
          InlineKeyboardButton("🇬🇧 الإنجليزية", callback_data="lang_trans_en"),
          InlineKeyboardButton("🇫🇷 الفرنسية", callback_data="lang_trans_fr"),
      ],
      [
          InlineKeyboardButton("🇪🇸 الإسبانية", callback_data="lang_trans_es"),
          InlineKeyboardButton("🇩🇪 الألمانية", callback_data="lang_trans_de"),
      ],
      [
          InlineKeyboardButton("🇮🇹 الإيطالية", callback_data="lang_trans_it"),
          InlineKeyboardButton("🇹🇷 التركية", callback_data="lang_trans_tr"),
      ],
      [
          InlineKeyboardButton("🇮🇳 الهندية", callback_data="lang_trans_hi"),
          InlineKeyboardButton("🇳🇱 الهولندية", callback_data="lang_trans_nl"),
      ],
      [
          InlineKeyboardButton(
              "🔙 رجوع لقسم الترجمة", callback_data="translation_menu"
          )
      ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await query.message.edit_text(
      "🌍 اختر اللغة المستهدفة لترجمة لغات العالم:", reply_markup=reply_markup
  )


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
      "`/activate <كود_الاشتراك>`"
  )
  await query.message.edit_text(
      activate_text, reply_markup=reply_markup, parse_mode="Markdown"
  )


async def my_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  user_id = query.from_user.id
  keyboard = [
      [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  sub_info = user_subscriptions.get(user_id, {"is_paid": False})

  if sub_info["is_paid"]:
    sub_text = (
        f"📊 **معلومات اشتراكك:**\n\n"
        f"• نوع الباقة: **مدفوعة**\n"
        f"• الرصيد المتبقي: 10 مقاطع باليوم\n"
        f"• تاريخ انتهاء الاشتراك: {sub_info.get('expiry_date', 'غير محدد')}"
    )
  else:
    used_seconds = free_tier_usage.get(user_id, 0)
    remaining_seconds = max(0, 180 - used_seconds)
    remaining_minutes = remaining_seconds // 60
    remaining_secs_only = remaining_seconds % 60
    sub_text = (
        f"📊 **معلومات اشتراكك:**\n\n"
        f"• نوع الباقة: **المجانية**\n"
        f"• الرصيد المتبقي: {remaining_minutes} دقائق و {remaining_secs_only} ثانية"
    )

  await query.message.edit_text(
      sub_text, reply_markup=reply_markup, parse_mode="Markdown"
  )


async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data

  if data == "dub_arabic_classic":
    response_msg = (
        "تم اختيار: دبلجة عربية فصحى.\n"
        "أهلاً بك، ارسل المقطع لنبدأ دبلجته.\n\n"
        f"📌 تأكد أن المقطع يتوافق مع شروط البوت: {CHANNEL_LINK}"
    )
  elif data == "trans_arabic_classic":
    response_msg = (
        "تم اختيار: ترجمة عربية فصحى.\n"
        "أهلاً بك، ارسل المقطع لنبدأ ترجمته.\n\n"
        f"📌 تأكد أن المقطع يتوافق مع شروط البوت: {CHANNEL_LINK}"
    )
  elif data.startswith("lang_dub_"):
    lang_code = data.replace("lang_dub_", "").upper()
    response_msg = (
        f"تم اختيار: دبلجة لغات العالم (اللغة: {lang_code}).\n"
        "ارسل المقطع لنبدأ العمل عليه.\n\n"
        f"📌 تأكد أن المقطع يتوافق مع شروط البوت: {CHANNEL_LINK}"
    )
  elif data.startswith("lang_trans_"):
    lang_code = data.replace("lang_trans_", "").upper()
    response_msg = (
        f"تم اختيار: ترجمة لغات العالم (اللغة: {lang_code}).\n"
        "ارسل المقطع لنبدأ العمل عليه.\n\n"
        f"📌 تأكد أن المقطع يتوافق مع شروط البوت: {CHANNEL_LINK}"
    )
  else:
    return

  await context.bot.send_message(
      chat_id=query.message.chat_id, text=response_msg
  )


async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not context.args:
    await update.message.reply_text(
        "❌ الصيغة غير صحيحة.\nالرجاء الاستخدام بهذا الشكل:\n`/activate"
        " <كود_الاشتراك>`",
        parse_mode="Markdown",
    )
    return

  code = context.args[0]
  user_id = update.message.from_user.id
  user_subscriptions[user_id] = {
      "is_paid": True,
      "expiry_date": "2026-10-15",
      "daily_clips_left": 10,
  }
  await update.message.reply_text(
      f"✅ تم تفعيل الكود `{code}` بنجاح! تم ترقية حسابك إلى الباقة المدفوعة.",
      parse_mode="Markdown",
  )


async def handle_incoming_media(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  user = update.message.from_user
  user_id = user.id
  sub_info = user_subscriptions.get(user_id, {"is_paid": False})

  if not sub_info["is_paid"]:
    video_duration_seconds = 30
    current_usage = free_tier_usage.get(user_id, 0)
    max_free_seconds = 180

    if current_usage >= max_free_seconds:
      expired_msg = (
          "بما أن انتهى اشتراكك أتمنى أعجبتك الباقة ونالت حُسن رضاك، نقدم لك خصماً"
          " على باقة الأسبوع من 15 ريال إلى 10 ريال، وينتهي العرض بعد يومين."
      )
      await update.message.reply_text(expired_msg)
      return

    free_tier_usage[user_id] = current_usage + video_duration_seconds

  is_spam_or_violation = False
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
      CallbackQueryHandler(
          dub_world_languages_list, pattern="^dub_world_languages_list$"
      )
  )
  app.add_handler(
      CallbackQueryHandler(
          trans_world_languages_list, pattern="^trans_world_languages_list$"
      )
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
          handle_selection,
          pattern="^(dub_arabic_classic|trans_arabic_classic|lang_dub_|lang_trans_)",
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
