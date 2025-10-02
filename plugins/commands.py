# ===================== Imports =====================
from pyrogram import filters, emoji
from pyrogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyromod import Client

from .admin_panel import admin_main
from .data import *
from .Myfilters import check_member, not_admin
from .message_manager import message_manager
# from .convert import (
#     get_glass_keyboard,
#     get_glass_price_text,
#     show_glass_panel,
#     handle_glass_messages,
# )

# ===================== Filters =====================
check_member_filter = filters.create(check_member)
not_admin_filter = filters.create(not_admin)

# ===================== Handlers =====================

@Client.on_message(filters.command(["start", "manage"]))
async def start_command(client, message):
    """هندلر برای کامند /start و /manage"""
    user_id = message.from_user.id  # ایدی کاربر    

    # حذف پیام‌های قبلی کاربر
    await message_manager.cleanup_user_messages(client, user_id, message.chat.id)

    # پیام خوشامد و دکمه شیشه‌ای برای ورود به تبدیل‌کننده
    welcome_text = (
        f"{emoji.SPARKLES} به صرافی پردیس خوش آمدید! {emoji.SPARKLES}\n\n"
        "از اینکه ما را برای خدمات ارزی انتخاب کردید سپاسگزاریم.\n"
        "در این ربات می‌توانید به راحتی و با اطمینان ارزهای خود را تبدیل کنید و از قیمت‌های لحظه‌ای مطلع شوید.\n\n"
        f"{emoji.MONEY_BAG} برای ورود به تبدیل‌کننده ارز، روی دکمه زیر کلیک کنید:"
    )
    converter_button = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"💱 ورود به تبدیل‌کننده",
                    callback_data="open_converter_panel"
                )
            ]
        ]
    )
    
    # ارسال پیام با مدیریت خودکار
    await message_manager.send_clean_message(
        client, message.chat.id, welcome_text, converter_button, user_id
    )

    # اگر ادمین است، پنل ادمین را هم نمایش بده
    if user_id in ADMINS:
        await admin_main(client, message)
    else:
        return

from .convert import (
    get_glass_keyboard,
    get_glass_price_text,
)

@Client.on_callback_query(filters.regex("^open_converter_panel$"))
async def open_converter_panel_callback(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی کاربر
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # پیام ورود به پنل تبدیل‌کننده با دکمه‌های انتخاب ارز
    text = (
        f"{emoji.BAR_CHART} قیمت‌های لحظه‌ای بازار:\n"
        f"{get_glass_price_text()}\n"
        f"لطفاً یکی از گزینه‌های زیر را برای تبدیل ارز انتخاب کنید:"
    )
    
    await message_manager.send_clean_message(
        client, chat_id, text, get_glass_keyboard(), user_id
    )

# هندلر برای انتخاب گزینه از پنل تبدیل ارز (تبدیل شیشه‌ای)
# @Client.on_message(filters.text & ~filters.command(["start", "manage"]))
# async def glass_converter_text_handler(client, message):
#     await handle_glass_messages(client, message)
