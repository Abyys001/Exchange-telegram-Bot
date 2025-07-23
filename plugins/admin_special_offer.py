from pathlib import Path
from os import getcwd
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyrogram import emoji

from .data import (
    admin_id, turn_all_offers_false, toman_form,
    able_offers, price_offers, get_state, CHANNEL_ID
)
from .offer_pic_generator import offer_draw

# ============== SPECIAL OFFER HANDLER ==============

OFFER_LABELS = [
    "💳 خرید ویژه از حساب",
    "💵 خرید ویژه نقدی",
    "💲 خرید ویژه تتر",
    "💳 فروش ویژه از حساب",
    "💵 فروش ویژه نقدی",
    "💲 فروش ویژه تتر",
]
FINALIZE_LABEL = "✅ نهایی‌سازی خرید/فروش ویژه"
BACK_LABEL = "🔙 بازگشت به منوی اصلی"
CANCEL_LABEL = "❌ انصراف"
CONFIRM_LABEL = "✅ بله، نهایی کن"
DECLINE_LABEL = "🔄 خیر، نیاز به تغییر دارم"

MAIN_TEXT = (
    "💷 خرید فروش تتر و پوند نقدی و حسابی\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "Mr. Mahdi    📞  +447533544249\n\n"
    "Ms. Kianian    📞  +989121894230\n\n"
    "Manager  📞  +447399990340\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "📌آدرس دفتر :\n"
    "<u>Office No7\n"
    "708A High Road\n"
    "North Finchley\n"
    "N129QL<u/>\n\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n\n"
    "مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد\n\n"
    "⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید ⛔"
)

def get_offer_keyboard():
    return ReplyKeyboardMarkup(
        [
            [OFFER_LABELS[0], OFFER_LABELS[1]],
            [OFFER_LABELS[2], OFFER_LABELS[3]],
            [OFFER_LABELS[4]],
            [OFFER_LABELS[5]],
            [FINALIZE_LABEL],
            [BACK_LABEL],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(CANCEL_LABEL)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_confirm_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(CONFIRM_LABEL), KeyboardButton(DECLINE_LABEL)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

async def special_offer(client, message, user_id=None, chat_id=None):
    """
    منوی خرید/فروش ویژه ادمین
    """
    keyboard = get_offer_keyboard()
    await client.send_message(
        message.chat.id,
        text="لطفاً نوع خرید یا فروش ویژه مورد نظر خود را انتخاب کنید:",
        reply_markup=keyboard
    )
    answer = await client.listen(message.chat.id)
    text = answer.text

    if text in OFFER_LABELS:
        await offer_handler(client, message, offer=text, user_id=user_id, chat_id=chat_id)
    elif text == FINALIZE_LABEL:
        await offer_finalize(client, message, user_id, chat_id)
    elif text == BACK_LABEL:
        await message.reply("✅ به منوی اصلی بازگشتید.")
    else:
        await message.reply("⚠️ لطفاً فقط از میان گزینه‌های موجود انتخاب کنید.")
        await special_offer(client, message, user_id, chat_id)

async def offer_handler(client, message, offer, user_id=None, chat_id=None):
    """
    ثبت قیمت برای یک پیشنهاد ویژه
    """
    await client.send_message(
        message.chat.id,
        text=f"💰 لطفاً قیمت {offer} را وارد کنید:",
        reply_markup=get_cancel_keyboard()
    )
    offer_price = await client.listen(message.chat.id)
    if offer_price.text == CANCEL_LABEL:
        turn_all_offers_false()
        await message.reply("⏪ عملیات لغو شد و به منوی اصلی بازگشتید.")
        return

    try:
        price = int(offer_price.text)
    except ValueError:
        await message.reply("❗️ لطفاً یک عدد معتبر وارد کنید.")
        await offer_handler(client, message, offer, user_id=user_id, chat_id=chat_id)
        return

    turn_all_offers_false()
    able_offers[offer] = True
    price_offers[offer] = price
    await message.reply(f"✅ قیمت {offer} با موفقیت به {toman_form(price)} تغییر یافت.")
    await special_offer(
        client,
        message,
        user_id or getattr(message, "from_user", None) and message.from_user.id,
        chat_id or getattr(message, "chat", None) and message.chat.id
    )

async def offer_finalize(client, message, user_id, chat_id):
    """
    نهایی کردن قیمت‌های ویژه و ارسال به کانال
    """
    try:
        offer_draw(get_state())
        image_path = Path(getcwd()) / f"./assets/offer{get_state()}.png"
        await message.reply_photo(image_path, caption=MAIN_TEXT)
    except Exception:
        await message.reply("⏳ لطفاً شکیبا باشید، در حال آماده‌سازی قیمت‌ها هستیم...")
        return

    ask_msg = await client.send_message(
        admin_id[0],
        text="آیا از نهایی‌سازی قیمت‌های ویژه اطمینان دارید؟",
        reply_markup=get_confirm_keyboard()
    )
    response = await client.listen(chat_id=admin_id[1], user_id=admin_id[0])

    if response.text == CONFIRM_LABEL:
        offer_draw(get_state())
        image_path = Path(getcwd()) / f"./assets/offer{get_state()}.png"
        await client.send_photo(CHANNEL_ID, image_path, caption=MAIN_TEXT)
        await client.delete_messages(admin_id[0], [response.id, ask_msg.id])
        await client.send_message(
            admin_id[0],
            text=f"🎉 قیمت‌های ویژه با موفقیت نهایی و به کانال ارسال شد {emoji.SPARKLES}"
        )
    elif response.text == DECLINE_LABEL:
        await client.delete_messages(admin_id[0], ask_msg.id)
        await client.send_message(admin_id[0], text="⏪ تغییرات ذخیره نشد و به منوی ویژه بازگشتید.")
