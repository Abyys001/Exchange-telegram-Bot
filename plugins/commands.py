# ===================== Imports =====================
from pyrogram import filters, emoji
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from pyromod import Client

from .admin_panel import admin_main
from .data import *
from .Myfilters import check_member, not_admin

# ===================== Filters =====================
check_member_filter = filters.create(check_member)
not_admin_filter = filters.create(not_admin)

# ===================== Handlers =====================

@Client.on_message(filters.command(["start", "manage"]))
async def start_command(client, message):
    """هندلر برای کامند /start و /manage"""
    user_id = message.from_user.id

    if user_id not in ADMINS:
        # کیبورد خوشامد برای کاربر عادی
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton(COMMANDS[2])]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        text = (
            f"🌟 به صرافی پردیس خوش آمدید! 🌟\n\n"
            "از حضور ارزشمند شما در جمع کاربران ما بسیار خرسندیم.\n"
            "در اینجا می‌توانید به آسانی و با اطمینان از خدمات متنوع مالی ما بهره‌مند شوید.\n"
            f"{emoji.SPARKLES} برای شروع کافیست از منوی زیر گزینه مورد نظر خود را انتخاب کنید. {emoji.FOLDED_HANDS}"
        )
        await client.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard,
        )
        return

    if user_id not in ADMINS:
        ADMINS.append(user_id)
    await admin_main(client, message)
