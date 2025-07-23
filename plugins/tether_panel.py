from pathlib import Path
from os import getcwd
from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from .offer_pic_generator import create_image_for_tether_offer
from .data import toman_form, tether_price, admin_id, CHANNEL_ID

STOP_KEY = "↩️ بازگشت"

FINAL_MESSAGE = (
    "💷 خرید فروش تتر و پوند نقدی و حسابی\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "Mr. Mahdi    📞  +447533544249\n\n"
    "Ms. Kianian    📞  +989121894230\n\n"
    "Manager  📞  +447399990340\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "📌آدرس دفتر :\n"
    "<u>Office No7\n"
    "North Finchley\n"
    "N129QL</u>\n\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n\n"
    "مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد\n\n"
    "⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید ⛔"
)

FINAL_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("ارتباط با کارشناس خرید و فروش 1", url="https://wa.me/447533544249")],
    [InlineKeyboardButton("ارتباط با کارشناس خرید و فروش 2", url="https://wa.me/989121894230")],
    [InlineKeyboardButton("مدیریت صرافی", url="https://wa.me/447399990340")],
    [
        InlineKeyboardButton("وب سایت", url="https://sarafipardis.co.uk/"),
        InlineKeyboardButton("اینستاگرام", url="https://www.instagram.com/sarafiipardis?igsh=MWxkZDVnY2J6djE5dg==")
    ],
    [
        InlineKeyboardButton("کانال تلگرام ما", url="https://t.me/sarafipardis2"),
        InlineKeyboardButton("بات تلگرامی ما", url="https://t.me/PardisSarafiBot")
    ]
])

TETHER_BUTTONS = [
    ["🟢 خرید تتر ریال", "🔴 فروش تتر ریال"],
    ["🟢 خرید تتر پوند", "🔴 فروش تتر پوند"]
]
TETHER_BUTTONS_TRANSLATE = {
    "🟢 خرید تتر ریال": "tether_buy_irr",
    "🔴 فروش تتر ریال": "tether_sell_irr",
    "🟢 خرید تتر پوند": "tether_buy_gbp",
    "🔴 فروش تتر پوند": "tether_sell_gbp"
}

MAIN_MENU_ACTIONS = [
    "📝 تنظیم قیمت‌ها",
    "✅ نهایی‌سازی",
    STOP_KEY,
]

FINAL_CONFIRM_ACTIONS = [
    "✅ بله",
    "❌ خیر"
]

def get_reply_keyboard(buttons, resize=True, one_time=True):
    """
    ساخت کیبورد ریپلای با دکمه‌های داده شده
    """
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(text) for text in row] if isinstance(row, list) else [KeyboardButton(row)]
            for row in buttons
        ],
        resize_keyboard=resize,
        one_time_keyboard=one_time
    )

async def tether_price_menu(client, message):
    """
    منوی انتخاب نوع قیمت تتر
    """
    keyboard = get_reply_keyboard(TETHER_BUTTONS + [[STOP_KEY]])
    await message.reply(
        "لطفاً نوع قیمت تتر مورد نظر خود را انتخاب کنید 👇",
        reply_markup=keyboard
    )
    response = await client.listen(chat_id=admin_id[0], user_id=admin_id[1])

    text = (response.text or "").strip()
    if text in TETHER_BUTTONS_TRANSLATE:
        await ask_price_value(client, message, tether_form=TETHER_BUTTONS_TRANSLATE[text])
    elif text == STOP_KEY:
        await tether_main_menu(client, message)
    else:
        await message.reply("❗️ لطفاً یکی از گزینه‌های موجود را انتخاب کنید.")
        await tether_price_menu(client, message)

async def tether_main_menu(client, message):
    """
    منوی اصلی تنظیمات تتر
    """
    keyboard = get_reply_keyboard([[action] for action in MAIN_MENU_ACTIONS])
    await message.reply(
        "👋 به منوی مدیریت قیمت‌های تتر خوش آمدید!\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )
    response = await client.listen(chat_id=admin_id[0], user_id=admin_id[1])

    text = (response.text or "").strip()
    if text == MAIN_MENU_ACTIONS[0]:
        await tether_price_menu(client, message)
    elif text == MAIN_MENU_ACTIONS[1]:
        await tether_final(client, message)
    elif text == MAIN_MENU_ACTIONS[2]:
        return
    else:
        await message.reply("❗️ گزینه انتخابی معتبر نیست. لطفاً مجدداً انتخاب کنید.")
        await tether_main_menu(client, message)

async def ask_price_value(client, message, tether_form):
    """
    دریافت مقدار قیمت از ادمین و ثبت آن
    """
    chat_id = message.chat.id
    await client.send_message(
        message.from_user.id,
        "لطفاً مقدار قیمت مورد نظر را به عدد وارد کنید (مثال: ۵۸۵۰۰):"
    )
    response = await client.listen(chat_id=admin_id[0], user_id=admin_id[1])

    text = (response.text or "").strip()
    if text == STOP_KEY:
        await tether_price_menu(client, message)
        return

    try:
        value = float(text)
        formatted_price = toman_form(int(value)) if value.is_integer() else str(value)
        tether_price[tether_form] = formatted_price
        await client.send_message(chat_id, text="✅ قیمت تتر با موفقیت ثبت و بروزرسانی شد.")
    except ValueError:
        await client.send_message(chat_id, text="⚠️ لطفاً فقط عدد معتبر وارد کنید.")
    except Exception:
        await client.send_message(chat_id, text="⛔️ مشکلی در ثبت قیمت پیش آمد. لطفاً دوباره تلاش کنید.")
    await tether_price_menu(client, message)

async def tether_final(client, message):
    """
    ارسال عکس و پیام نهایی به ادمین و کانال
    """
    image_path = Path(getcwd()) / create_image_for_tether_offer()
    await message.reply_photo(image_path, caption=FINAL_MESSAGE, reply_markup=FINAL_KEYBOARD)

    keyboard = get_reply_keyboard([FINAL_CONFIRM_ACTIONS])
    await message.reply(
        "آیا از نهایی‌سازی و ارسال قیمت‌ها به کانال اطمینان دارید؟\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )
    response = await client.listen(chat_id=admin_id[0], user_id=admin_id[1])

    text = (response.text or "").strip()
    if text == FINAL_CONFIRM_ACTIONS[0]:
        await message.reply("⏳ در حال نهایی‌سازی و ارسال به کانال...")
        await client.send_photo(CHANNEL_ID, image_path, caption=FINAL_MESSAGE, reply_markup=FINAL_KEYBOARD)
        await message.reply("✅ نهایی‌سازی با موفقیت انجام شد و قیمت‌ها به کانال ارسال گردید!")
    elif text == FINAL_CONFIRM_ACTIONS[1]:
        await message.reply("❌ عملیات نهایی‌سازی لغو شد.")
        return
    else:
        await message.reply("لطفاً یکی از گزینه‌های زیر را انتخاب کنید.")
        await tether_final(client, message)
