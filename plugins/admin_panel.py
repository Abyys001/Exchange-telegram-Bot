from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyromod import Client

from .data import COMMANDS, insert_admin_stuff_to_data
from .admin_news import news_handler
from .admin_special_offer import special_offer
from .admin_finalize import finalize_prices
from .tether_panel import tether_main_menu

# ============== ADMIN panels ==============

@Client.on_callback_query("back_to_main_menu")
async def back_to_main_menu(client, message):
    await admin_main(client, message)

async def admin_main(client, message):
    """
    Entry point for admin panel. Saves admin info and shows the panel.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    await insert_admin_stuff_to_data(user_id, chat_id)
    await admin_panel(client, message, user_id, chat_id)

async def admin_panel(client, message, *args):
    """
    Show main admin panel with options.
    """
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton(COMMANDS[0])],
            [KeyboardButton(COMMANDS[1])],
            [KeyboardButton(COMMANDS[2])],
            [KeyboardButton(COMMANDS[3])],
            [KeyboardButton(COMMANDS[4])],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    text = (
        "👤 به پنل مدیریت صرافی پردیس خوش آمدید.\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    )
    answer = await client.ask(message.chat.id, text=text, reply_markup=keyboard)

    if answer.text in COMMANDS:
        if answer.text == COMMANDS[0]:
            from .data import change_price
            await change_price(client, message)
        elif answer.text == COMMANDS[1]:
            await special_offer(client, message, args[0], args[1])
        elif answer.text == COMMANDS[2]:
            await news_handler(client, message)
        elif answer.text == COMMANDS[3]:
            await tether_main_menu(client, message)
            await admin_main(client, message)
        elif answer.text == COMMANDS[4]:
            await finalize_prices(client, message, args[0], args[1])
    else:
        await message.reply(
            "❗ گزینه نامعتبر است.\n"
            "لطفاً فقط از میان گزینه‌های موجود انتخاب کنید."
        )
