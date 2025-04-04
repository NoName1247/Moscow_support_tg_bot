import datetime
import threading
from time import sleep

from psycopg2.extras import DateRange
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, filters
from database import *
from config import Settings

(STAGE1, STAGE2, STAGE3, STAGE4) = range(4)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7886432045:AAGHhX3NHrg91BpoHV3mZFDi2ffoY_6yHFc"
CHAT_ID = -1002451009334


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(open("info.txt", "r", encoding="utf-8").read())


def save(user_data, telegram_id, username, request_text):
    the_daterange = user_data["dates"].split(" - ")
    the_daterange_lower = datetime.datetime.strptime(the_daterange[0], '%d.%m.%Y').date()
    the_daterange_upper = datetime.datetime.strptime(the_daterange[1], '%d.%m.%Y').date()
    the_daterange = DateRange(the_daterange_lower, the_daterange_upper)
    return insert_request(user_data["name"], "@"+username, telegram_id, user_data["rank"], user_data["competition"], the_daterange, request_text, 0, 0)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте, Лидер!")
    await update.message.reply_text("Пожалуйста, введите ваше ФИО:")
    return STAGE1


async def stage1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        context.user_data["name"] = update.message.text
        await update.message.reply_text("Введите ваш статус (полуфиналист, финалист, победитель и т.д.):")
        return STAGE2
    return STAGE1


async def stage2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        context.user_data["rank"] = update.message.text
        await update.message.reply_text("Введите название мероприятия:")
        return STAGE3
    return STAGE2


async def stage3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        context.user_data["competition"] = update.message.text
        await update.message.reply_text("Укажите время пребывания в Москве (дд.мм.гггг - дд.мм.гггг):")
        return STAGE4
    return STAGE3


async def stage4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        if len(update.message.text.split(" - ")) == 2 and len(update.message.text.split(".")) == 5:
            context.user_data["dates"] = update.message.text
            await update.message.reply_text("Опишите ваш проблему:")
            return ConversationHandler.END
    return STAGE4

async def send_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    request_text = update.message.text

    bd_id = save(context.user_data, user.id, user.username, request_text)

    message = (
        f"📌 Новый запрос от {context.user_data["name"]}!\n"
        f"Статус: {context.user_data["rank"]}, мероприятия: {context.user_data["competition"]}\n"
        f"Дата: {context.user_data["dates"]}\n"
        f"Проблема: {request_text}\n\n"
        f"Адрес пользователя: @{user.username}"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Принять", callback_data=f"accept@{bd_id}@{user.id}@{user.username}")],
    ]

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("✅ Ваш запрос отправлен. Ожидайте ответа!")
    return ConversationHandler.END


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sup_id, rate = "0", "0"
    if query.data.split("@")[0] == "rate":
        action, bd_id, rate, sup_id = query.data.split('@')
        leader_id = 0
        username = ""
    elif query.data.split("@")[0] == "finish":
        action, bd_id, leader_id, username, sup_id = query.data.split('@')
    else:
        action, bd_id, leader_id, username = query.data.split('@')
        leader_id = int(leader_id)
    if action == "rate":
        if select_request_status(int(bd_id)) != 4:
            print(change_status(int(bd_id), 4))
            karma = select_karma(int(sup_id))
            print(change_karma(int(sup_id), int(karma) + int(rate)))
    elif action == "finish":
        if select_request_status(int(bd_id)) != 0:
            print(change_status(int(bd_id), 3))
            keyboard = [
                [InlineKeyboardButton("🟢 5", callback_data=f"rate@{bd_id}@5@{sup_id}"),
                InlineKeyboardButton("🟡 4", callback_data=f"rate@{bd_id}@4@{sup_id}"),
                InlineKeyboardButton("🟠 3", callback_data=f"rate@{bd_id}@3@{sup_id}"),
                InlineKeyboardButton("🟤 2", callback_data=f"rate@{bd_id}@2@{sup_id}"),
                InlineKeyboardButton("🔴 1", callback_data=f"rate@{bd_id}@1@{sup_id}")]
            ]
            await context.bot.send_message(
                chat_id=leader_id,
                text=f"Пожалуйста, оцените карму Дежурного!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif action == "retry":
        if select_request_status(int(bd_id)) != 3:
            print(change_status(int(bd_id), 0))
            print(change_support(int(bd_id), 0))
            await context.bot.send_message(
                chat_id=leader_id,
                text=f"❗ Приносим свои извинения. Ваш запрос будет отправлен повторно."
            )
            res = select_req(int(bd_id))
            message = (
                f"📌 Запрос от {res[0]}!\n"
                f"Статус: {res[1]}, соревнование: {res[2]}\n"
                f"Даты: {str(res[3]).replace("-", ".").replace(", ", " - ")[1:-1]}\n"
                f"Запрос: {res[4]}\n\n"
                f"Адрес пользователя: {res[5]}"
            )
            keyboard = [
                [InlineKeyboardButton("✅ Принять", callback_data=f"accept@{bd_id}@{query.from_user.id}@{query.from_user.username}")],
            ]
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif action == "submit":
        print(change_status(int(bd_id), 2))
        print(change_support(int(bd_id), query.from_user.id))
        print(insert_new_support("@" + query.from_user.username, query.from_user.id))
        message = (
            f"✅ Запрос принят!\n"
                 f"Дежурный: @{query.from_user.username}\n"
                 f"Свяжитесь с пользователем @{username}."
        )
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )
        await context.bot.send_message(
            chat_id=leader_id,
            text=f"Ваш запрос принял Дежурный @{query.from_user.username}!\n"
                 f"Свяжитесь с ним для получения помощи."
        )
        keyboard = [
            [InlineKeyboardButton("✅ Да", callback_data=f"finish@{bd_id}@{leader_id}@{username}@{query.from_user.id}"),
             InlineKeyboardButton("❌ Нет", callback_data=f"retry@{bd_id}@{leader_id}@{username}")]
        ]
        await context.bot.send_message(
            chat_id=leader_id,
            text=f"Смог ли Дежурный помочь вам?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif action == "denied":
        print(change_status(int(bd_id), 0))
    elif action == "accept":
        stat = select_request_status(int(bd_id))
        if stat == 0:
            print(change_status(int(bd_id), 1))
            keyboard = [
                [InlineKeyboardButton("✅ Да", callback_data=f"submit@{bd_id}@{leader_id}@{username}"),
                 InlineKeyboardButton("❌ Нет", callback_data=f"denied@{bd_id}@{leader_id}@{username}")]
            ]
            await context.bot.send_message(
                chat_id=leader_id,
                text=f"На ваш запрос откликнулся {query.from_user.username},\n"
                     f"Карма: {select_karma(query.from_user.id)}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        elif stat == 2:
            await query.edit_message_text(
                text=f"❗ Данный запрос уже обрабатывается другим Дежурным!"
            )
        else:
            await query.edit_message_text(
                text=f"❗ Запрос уже не актуален!"
            )


async def every_week(update: Update, context: ContextTypes.DEFAULT_TYPE, test: bool = False):
    while True:
        if not test:
            sleep(604800)
        top_k = select_top_of_karma()
        mess = "Недельный рейтинг:"
        for i in range(len(top_k)):
            mess += f"\n{i+1}: {top_k[i][0]} - {top_k[i][1]}"
        message = (
            mess
        )
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=message,
        )
        if test:
            break


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler("info", info),
                      CommandHandler("test", lambda update, context: every_week(update=update, context=context, test=True))],
        states={
            STAGE1: [MessageHandler(filters.TEXT & ~filters.COMMAND, stage1)],
            STAGE2: [MessageHandler(filters.TEXT & ~filters.COMMAND, stage2)],
            STAGE3: [MessageHandler(filters.TEXT & ~filters.COMMAND, stage3)],
            STAGE4: [MessageHandler(filters.TEXT & ~filters.COMMAND, stage4)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_request))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()


if __name__ == '__main__':
    main()
