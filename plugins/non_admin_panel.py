from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pathlib import Path
from os import getcwd

from .pic_generator import draw
from .data import let_keyboard, COMMANDS
from pyromod import Client
from .Myfilters import not_admin

not_admin_filter = filters.create(not_admin)

CONTACT_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("ارتباط با کارشناس ۱ خرید و فروش", url="https://wa.me/447533544249")],
    [InlineKeyboardButton("ارتباط با کارشناس ۲ خرید و فروش", url="https://wa.me/989121894230")],
    [InlineKeyboardButton("مدیریت صرافی", url="https://wa.me/447399990340")],
    [
        InlineKeyboardButton("وب‌سایت", url="https://sarafipardis.co.uk/"),
        InlineKeyboardButton("اینستاگرام", url="https://www.instagram.com/sarafiipardis?igsh=MWxkZDVnY2J6djE5dg==")
    ],
    [
        InlineKeyboardButton("کانال تلگرام", url="https://t.me/sarafipardis"),
        InlineKeyboardButton("ربات تلگرام", url="https://t.me/PardisSarafiBot")
    ],
])

MAIN_TEXT = (
    "💷 خرید فروش تتر و پوند نقدی و حسابی\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "Mr. Mahdi    📞  +447533544249\n\n"
    "Ms. Kianian    📞  +989121894230\n\n"
    "Manager  📞  +447399990340\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "📌آدرس دفتر:\n"
    "<u>Office A\n"
    "North Finchley\n"
    "N12 9QL</u>\n\n"
    "🔘 ساعات کاری:\n"
    "از دوشنبه تا جمعه از ساعت 🕤۹:۳۰ الی 🕠۱۷:۳۰\n\n"
    "روزهای شنبه از ساعت 🕥۱۰:۳۰ الی🕝 ۱۴:۳۰\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n\n"
    "مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد\n\n"
    "⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید⛔"
)

@Client.on_message(filters.text & filters.private & not_admin_filter)
async def non_admin(client, message):
    await contact_us(client, message)

async def contact_us(client, message):
    """
    ارسال اطلاعات تماس و تصویر قیمت‌ها برای کاربران غیرادمین
    """
    try:
        draw()  # تولید تصویر قیمت‌ها
        image_path = Path(getcwd()) / "assets/prices.png"
        kwargs = {
            "photo": image_path,
            "caption": MAIN_TEXT
        }
        if let_keyboard:
            kwargs["reply_markup"] = CONTACT_KEYBOARD
        await message.reply_photo(**kwargs)
    except Exception as e:
        await message.reply(f"[contact_us] Error: {e}")