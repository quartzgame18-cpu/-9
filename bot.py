from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = "ВСТАВЬ_ТОКЕН"
ADMIN_ID = 123456789

user_data = {}
admin_reply_target = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("❓ Вопрос", callback_data="question")],
        [InlineKeyboardButton("⚖️ Обжалование", callback_data="appeal")],
        [InlineKeyboardButton("🐞 Баг", callback_data="bug")]
    ]
    await update.message.reply_text("👋 Выберите категорию:", reply_markup=InlineKeyboardMarkup(keyboard))

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "question":
        user_data[uid] = {"type": "question", "step": 1}
        await query.message.reply_text("Введите ваш Ник:")
    elif query.data == "appeal":
        user_data[uid] = {"type": "appeal", "step": 1}
        await query.message.reply_text("Ваш Ник:")
    elif query.data == "bug":
        user_data[uid] = {"type": "bug", "step": 1}
        await query.message.reply_text("Ваш Ник:")

async def callback_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_reply_target
    query = update.callback_query
    await query.answer()
    admin_reply_target = int(query.data.split("_")[1])
    await query.message.reply_text("✉️ Напишите ответ пользователю:")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_reply_target
    uid = update.message.from_user.id
    text = update.message.text

    if uid == ADMIN_ID and admin_reply_target is not None:
        await context.bot.send_message(admin_reply_target, f"📩 Ответ от администрации: {text}")
        admin_reply_target = None
        await update.message.reply_text("✅ Ответ отправлен.")
        return

    if uid not in user_data:
        return

    data = user_data[uid]

    if data["type"] == "question":
        if data["step"] == 1:
            data["nick"] = text
            data["step"] = 2
            await update.message.reply_text("Ваш вопрос:")
        else:
            data["question"] = text
            await update.message.reply_text("✅ Вопрос отправлен руководству.")
            user_data.pop(uid)

    elif data["type"] == "appeal":
        if data["step"] == 1:
            data["nick"] = text
            data["step"] = 2
            await update.message.reply_text("Наказание и причина:")
        elif data["step"] == 2:
            data["reason"] = text
            data["step"] = 3
            await update.message.reply_text("Телеграмм юзернейм:")
        else:
            data["tg"] = text
            await update.message.reply_text("✅ Обжалование отправлено руководству.")
            user_data.pop(uid)

    elif data["type"] == "bug":
        if data["step"] == 1:
            data["nick"] = text
            data["step"] = 2
            await update.message.reply_text("Обнаруженный баг:")
        elif data["step"] == 2:
            data["bug"] = text
            data["step"] = 3
            await update.message.reply_text("Как вы его обнаружили:")
        else:
            data["how"] = text
            await update.message.reply_text("🐞 Передано тестировщикам.")
            user_data.pop(uid)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu_handler, pattern="^(question|appeal|bug)$"))
app.add_handler(CallbackQueryHandler(callback_reply, pattern="^reply_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

print("Bot started...")
app.run_polling()
