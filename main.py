import nest_asyncio
import asyncio
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

nest_asyncio.apply()

# 🔐 توكن البوت
# ⚠️ تذكر أن تضع توكن البوت الخاص بك هنا
BOT_TOKEN = "5854871500:AAFveHeJROSrtci4w_COYeyosQsc2hEfjbY" 

# 📊 قاموس لتخزين رصيد النجوم للمستخدمين (لأغراض العرض، يفضل استخدام قاعدة بيانات في الإنتاج)
user_balances = {}

# 🛍️ قاموس لتخزين السلع المتاحة للشراء
available_items = {
    "item_1": {"title": "سلعة عشوائية 1", "cost": 100, "content": "محتوى السلعة العشوائية رقم 1."},
    "item_2": {"title": "سلعة عشوائية 2", "cost": 200, "content": "محتوى السلعة العشوائية رقم 2."},
    "item_3": {"title": "سلعة عشوائية 3", "cost": 300, "content": "محتوى السلعة العشوائية رقم 3."},
    "item_4": {"title": "سلعة عشوائية 4", "cost": 400, "content": "محتوى السلعة العشوائية رقم 4."},
    "item_5": {"title": "سلعة عشوائية 5", "cost": 500, "content": "محتوى السلعة العشوائية رقم 5."},
    "item_6": {"title": "سلعة عشوائية 6", "cost": 600, "content": "محتوى السلعة العشوائية رقم 6."},
    "item_7": {"title": "سلعة عشوائية 7", "cost": 700, "content": "محتوى السلعة العشوائية رقم 7."},
    "item_8": {"title": "سلعة عشوائية 8", "cost": 800, "content": "محتوى السلعة العشوائية رقم 8."},
    "item_9": {"title": "سلعة عشوائية 9", "cost": 900, "content": "محتوى السلعة العشوائية رقم 9."},
    "item_10": {"title": "سلعة عشوائية 10", "cost": 1000, "content": "محتوى السلعة العشوائية رقم 10."},
}

# 📌 أمر /start - القائمة الرئيسية الجديدة
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.mention_html()

    if user_id not in user_balances:
        user_balances[user_id] = 0

    keyboard = [
        [InlineKeyboardButton("💬 للتواصل", url="https://t.me/a4_m_s"), InlineKeyboardButton("📢 قناة البوت", url="https://t.me/apps1ali")],
        [InlineKeyboardButton("🛍️ متجر السلع", callback_data='show_items')],
        [InlineKeyboardButton("⭐ رصيدي الحالي", callback_data='show_balance')],
        [InlineKeyboardButton("💰 شراء النجوم", callback_data='buy_stars')],
        [InlineKeyboardButton("❓ مساعدة", callback_data='help_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        rf"مرحباً بك {user_name}! 🚀 في بوت السلع العشوائية."
        f"\n\nرصيدك الحالي: **{user_balances.get(user_id, 0)} ⭐**"
        f"\n\n👇 اشترك في القناة وتواصل معنا من الأزرار أدناه!",
        reply_markup=reply_markup
    )

# 🛍️ عرض متجر السلع
async def show_items_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = []
    for item_id, item_info in available_items.items():
        keyboard.append([InlineKeyboardButton(f"{item_info['title']} ({item_info['cost']} ⭐)", callback_data=f'view_item_{item_id}')])

    keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="اختر السلعة التي تود شرائها:", reply_markup=reply_markup)

# 📦 عرض تفاصيل السلعة ومحاولة الشراء
async def view_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    item_id = query.data.replace('view_item_', '')

    if item_id not in available_items:
        await query.edit_message_text("❌ السلعة غير موجودة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للمتجر", callback_data='show_items')]]))
        return

    item_info = available_items[item_id]
    user_stars = user_balances.get(user_id, 0)

    message_text = (
        f"🛍️ **{item_info['title']}**\n\n"
        f"💰 **التكلفة:** {item_info['cost']} ⭐\n\n"
        f"🌟 **رصيدك الحالي:** {user_stars} ⭐\n\n"
    )

    if user_stars >= item_info['cost']:
        keyboard = [[InlineKeyboardButton(f"شراء السلعة بـ {item_info['cost']} ⭐", callback_data=f'buy_item_{item_id}')]]
    else:
        keyboard = [[InlineKeyboardButton("شراء المزيد من النجوم 💰", callback_data='buy_stars')]]

    keyboard.append([InlineKeyboardButton("🔙 العودة للمتجر", callback_data='show_items')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')

# 🔓 شراء السلعة بعد الدفع بالنجوم
async def buy_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    item_id = query.data.replace('buy_item_', '')

    if item_id not in available_items:
        await query.edit_message_text("❌ السلعة غير موجودة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للمتجر", callback_data='show_items')]]))
        return

    item_info = available_items[item_id]
    user_stars = user_balances.get(user_id, 0)

    if user_stars >= item_info['cost']:
        user_balances[user_id] -= item_info['cost']
        await query.edit_message_text(
            f"✅ تم شراء السلعة بنجاح! تم خصم {item_info['cost']} ⭐ من رصيدك.\n\n"
            f"🌟 **رصيدك الحالي:** {user_balances[user_id]} ⭐\n\n"
            f"--- **{item_info['title']}** ---\n\n"
            f"{item_info['content']}\n\n"
            f"--- انتهى المحتوى ---",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للمتجر", callback_data='show_items')]]),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            "عذراً، رصيدك من النجوم غير كافٍ لشراء هذه السلعة 😔."
            f"\n\n🌟 رصيدك الحالي: {user_stars} ⭐",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("شراء المزيد من النجوم 💰", callback_data='buy_stars')],
                [InlineKeyboardButton("🔙 العودة للمتجر", callback_data='show_items')]
            ])
        )

# ⭐ عرض رصيد النجوم للمستخدم
async def show_balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    current_balance = user_balances.get(user_id, 0)
    await query.edit_message_text(
        f"🌟 رصيدك الحالي هو: **{current_balance} ⭐**",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 شراء المزيد من النجوم", callback_data='buy_stars')], [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='main_menu')]]),
        parse_mode='Markdown'
    )

# 💰 عرض باقات النجوم للشراء
async def buy_stars_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("100 ⭐", callback_data='pay_100'), InlineKeyboardButton("200 ⭐", callback_data='pay_200')],
        [InlineKeyboardButton("300 ⭐", callback_data='pay_300'), InlineKeyboardButton("400 ⭐", callback_data='pay_400')],
        [InlineKeyboardButton("500 ⭐", callback_data='pay_500'), InlineKeyboardButton("600 ⭐", callback_data='pay_600')],
        [InlineKeyboardButton("700 ⭐", callback_data='pay_700'), InlineKeyboardButton("800 ⭐", callback_data='pay_800')],
        [InlineKeyboardButton("900 ⭐", callback_data='pay_900'), InlineKeyboardButton("1000 ⭐", callback_data='pay_1000')],
    ]
    keyboard.append([InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("اختر باقة النجوم التي تريد شراءها:", reply_markup=reply_markup)

# ❓ قائمة المساعدة
async def help_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    help_message = (
        "مرحباً بك في قسم المساعدة!\n\n"
        "هذا البوت يتيح لك:\n"
        "1. **شراء النجوم:** استخدم النجوم لشراء السلع من المتجر.\n"
        "2. **متجر السلع:** تصفح واشترِ السلع الحصرية باستخدام نجومك.\n"
        "3. **رصيدي:** تحقق من عدد النجوم المتبقية لديك.\n\n"
        "إذا واجهت أي مشكلة، يرجى التواصل معنا عبر الزر أدناه."
    )
    keyboard = [
        [InlineKeyboardButton("تواصل معنا", url="https://t.me/a4_m_s")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode='Markdown')

# 🔙 العودة للقائمة الرئيسية
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.mention_html()

    if user_id not in user_balances:
        user_balances[user_id] = 0

    keyboard = [
        [InlineKeyboardButton("💬 للتواصل", url="https://t.me/a4_m_s"), InlineKeyboardButton("📢 قناة البوت", url="https://t.me/apps1ali")],
        [InlineKeyboardButton("🛍️ متجر السلع", callback_data='show_items')],
        [InlineKeyboardButton("⭐ رصيدي الحالي", callback_data='show_balance')],
        [InlineKeyboardButton("💰 شراء النجوم", callback_data='buy_stars')],
        [InlineKeyboardButton("❓ مساعدة", callback_data='help_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        rf"أهلاً بك مجدداً {user_name}! 🚀\n\n"
        f"رصيدك الحالي: **{user_balances.get(user_id, 0)} ⭐**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# 💳 الضغط على باقة النجوم
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        amount_in_stars = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.edit_message_text(text="❌ حدث خطأ في اختيار المبلغ. حاول مرة أخرى.")
        return

    title = f"باقة {amount_in_stars} نجمة"
    description = f"شراء {amount_in_stars} من نجوم تيليجرام."
    payload = f"StarsPayment-{query.from_user.id}-{amount_in_stars}-{uuid.uuid4()}"
    currency = "XTR"
    prices = [{"label": f"{amount_in_stars} نجمة", "amount": amount_in_stars}]

    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",
        currency=currency,
        prices=prices,
        start_parameter="telegram-stars-payment"
    )

# ✅ الموافقة على الدفع قبل إتمامه
async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("StarsPayment-"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="🚫 حدث خطأ أثناء معالجة الدفع.")

# 🎉 عند الدفع الناجح
async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    stars_amount = update.message.successful_payment.total_amount

    user_balances[user_id] = user_balances.get(user_id, 0) + stars_amount

    await update.message.reply_text(
        f"🎉 شكراً لك! تم شحن حسابك بـ {stars_amount} نجمة بنجاح.\n"
        f"🌟 رصيدك الحالي هو: **{user_balances[user_id]} ⭐**",
        parse_mode='Markdown'
    )
    await update.message.reply_text(
        "يمكنك الآن استخدام نجومك لشراء السلع من المتجر.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍️ الذهاب للمتجر", callback_data='show_items')],
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data='main_menu')]
        ])
    )

# 🧠 تشغيل البوت
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(show_items_callback, pattern='^show_items$'))
    app.add_handler(CallbackQueryHandler(view_item_callback, pattern='^view_item_'))
    app.add_handler(CallbackQueryHandler(buy_item_callback, pattern='^buy_item_'))
    app.add_handler(CallbackQueryHandler(show_balance_callback, pattern='^show_balance$'))
    app.add_handler(CallbackQueryHandler(buy_stars_callback, pattern='^buy_stars$'))
    app.add_handler(CallbackQueryHandler(help_menu_callback, pattern='^help_menu$'))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern='^main_menu$'))

    # Star payment handlers
    app.add_handler(CallbackQueryHandler(button_callback, pattern='^pay_'))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    print("✅ البوت يعمل الآن وينتظر أوامر من تيليجرام...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
