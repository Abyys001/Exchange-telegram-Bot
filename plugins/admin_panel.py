from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from ..main import app
from pyrogram import Client, filters

from .data import COMMANDS, insert_admin_stuff_to_data, ADMINS
from .admin_news import news_handler
from .admin_special_offer import special_offer
from .admin_finalize import finalize_prices
from .tether_panel import tether_main_menu
from .message_manager import message_manager, get_home_button

# ============== ADMIN panels ==============

@Client.on_callback_query(filters.regex("^back_to_main_menu$"))
async def back_to_main_menu(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)

    await admin_panel(client, callback_query.message, user_id, chat_id)

async def admin_main(client, message):
    """
    Entry point for admin panel. Only allows ADMINS to enter.
    Saves admin info and shows the panel.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    # فقط ادمین‌ها اجازه ورود دارند
    if user_id not in ADMINS:
        await message.reply("⛔ شما دسترسی به پنل مدیریت ندارید.")
        return

    # ذخیره اطلاعات ادمین برای استفاده بعدی
    await insert_admin_stuff_to_data(user_id, chat_id)
    await admin_panel(client, message, user_id, chat_id)

async def admin_panel(client, message, *args):
    """
    Show main admin panel with options.
    """
    user_id = args[0] if args else None
    chat_id = args[1] if len(args) > 1 else None

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(COMMANDS[0], callback_data="admin_change_price")],
        [InlineKeyboardButton(COMMANDS[1], callback_data="admin_special_offer")],
        [InlineKeyboardButton(COMMANDS[2], callback_data="admin_news")],
        [InlineKeyboardButton(COMMANDS[3], callback_data="admin_tether")],
        [InlineKeyboardButton(COMMANDS[4], callback_data="admin_finalize")],
        [get_home_button()]
    ])

    text = (
        "👤 به پنل مدیریت صرافی پردیس خوش آمدید.\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    if user_id and chat_id:
        await message_manager.send_clean_message(client, chat_id, text, keyboard, user_id)
    else:
        await message.reply(text=text, reply_markup=keyboard)

# ============== Callback Handlers ==============

@Client.on_callback_query(filters.regex("^admin_change_price$"))
async def admin_change_price_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)

    from .data import change_price
    await change_price(client, callback_query.message)

@Client.on_callback_query(filters.regex("^admin_special_offer$"))
async def admin_special_offer_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)

    await special_offer(client, callback_query.message, user_id, chat_id)

@Client.on_callback_query(filters.regex("^admin_news$"))
async def admin_news_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)

    await news_handler(client, callback_query.message)

@Client.on_callback_query(filters.regex("^admin_tether$"))
async def admin_tether_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)

    await tether_main_menu(client, callback_query.message)

@Client.on_callback_query(filters.regex("^admin_finalize$"))
async def admin_finalize_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)

    await finalize_prices(client, callback_query.message, user_id, chat_id)
