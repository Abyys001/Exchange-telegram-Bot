from pathlib import Path
from os import getcwd
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from .data import send_data, CHANNEL_ID, admin_id, get_state, turn_all_calls_false
from pyrogram import emoji
from .pic_generator import draw
from .offer_pic_generator import offer_draw

FINAL_MESSAGE = """
💷 خرید فروش تتر و پوند نقدی و حسابی
🔺🔺🔺🔺🔺🔺🔺🔺🔺
Mr. Mahdi    📞  +447533544249

Ms. Kianian    📞  +989121894230

Manager  📞  +447399990340
🔺🔺🔺🔺🔺🔺🔺🔺🔺
📌آدرس دفتر :
<u>Office A
708A High Road
North Finchley
N129QL<u/>

🔺🔺🔺🔺🔺🔺🔺🔺🔺

مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد

⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید ⛔
"""

FINAL_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("ارتباط با کارشناس خرید و فروش 1", url="https://wa.me/447533544249")],
    [InlineKeyboardButton("ارتباط با کارشناس خرید و فروش 2", url="https://wa.me/989121894230")],
    [InlineKeyboardButton("مدیریت صرافی", url="https://wa.me/447399990340")],
    [
        InlineKeyboardButton("وب سایت", url="https://sarafipardis.co.uk/"),
        InlineKeyboardButton("اینستاگرام", url="https://www.instagram.com/sarafiipardis")
    ],
    [
        InlineKeyboardButton("کانال تلگرام ما", url="https://t.me/sarafipardis"),
        InlineKeyboardButton("بات تلگرامی ما", url="https://t.me/PardisSarafiBot")
    ]
])

def get_final_confirm_keyboard():
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton("✅ بله، نهایی کن"),
                KeyboardButton("🔄 خیر، نیاز به تغییر دارم")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

async def _send_image_with_caption(message_func, image_path, caption=FINAL_MESSAGE, keyboard=FINAL_KEYBOARD):
    try:
        await message_func(image_path, caption=caption, reply_markup=keyboard)
        return True
    except Exception:
        return False

async def _get_admin_confirmation(client, chat_id, user_id, prompt):
    ask_user = await client.send_message(
        admin_id[0],
        prompt,
        reply_markup=get_final_confirm_keyboard()
    )
    response = await client.listen(chat_id=chat_id, user_id=user_id)
    return ask_user, response

async def finalize_prices(client, message, chat_id, id_of_chat):
    data_folder = Path(getcwd())
    image_path = data_folder / "assets/prices.png"

    draw()
    sent = await _send_image_with_caption(
        message.reply_photo,
        image_path
    )
    if not sent:
        await message.reply("⏳ لطفاً کمی صبر کنید، در حال آماده‌سازی اطلاعات هستیم...")
        return

    ask_user, response = await _get_admin_confirmation(
        client, id_of_chat, chat_id, "آیا از نهایی کردن قیمت‌ها اطمینان دارید؟"
    )

    if response.text == "✅ بله، نهایی کن":
        send_data()
        draw()
        await _send_image_with_caption(
            lambda img, **kwargs: client.send_photo(CHANNEL_ID, img, **kwargs),
            image_path
        )
        await client.send_message(
            chat_id,
            f"✅ قیمت‌ها با موفقیت نهایی شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}\n\nدر صورت نیاز به تغییر، می‌توانید مجدداً اقدام کنید."
        )
        turn_all_calls_false()
    else:
        await client.send_message(
            chat_id,
            "🔄 متوجه شدم! هر زمان آماده بودید، می‌توانید ادامه دهید یا تغییرات خود را اعمال کنید."
        )

    await client.delete_messages(chat_id, [ask_user.id, response.id])

async def finalize_special_offers(client, message, chat_id, id_of_chat):
    state = get_state()
    data_folder = Path(getcwd())
    image_path = data_folder / f"assets/offer{state}.png"

    offer_draw(state)
    sent = await _send_image_with_caption(
        message.reply_photo,
        image_path
    )
    if not sent:
        await message.reply("⏳ لطفاً کمی صبر کنید، در حال آماده‌سازی اطلاعات ویژه هستیم...")
        return

    ask_user, response = await _get_admin_confirmation(
        client, id_of_chat, chat_id, "آیا از نهایی کردن قیمت‌های ویژه اطمینان دارید؟"
    )

    if response.text == "✅ بله، نهایی کن":
        offer_draw(state)
        await _send_image_with_caption(
            lambda img, **kwargs: client.send_photo(CHANNEL_ID, img, **kwargs),
            image_path
        )
        await client.send_message(
            chat_id,
            f"🎉 قیمت‌های ویژه با موفقیت نهایی شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}\n\nدر صورت نیاز به تغییر، می‌توانید مجدداً اقدام کنید."
        )
    else:
        await client.send_message(
            chat_id,
            "🔄 مشکلی نیست! هر زمان خواستید می‌توانید ادامه دهید یا تغییرات خود را ثبت کنید."
        )

    await client.delete_messages(chat_id, [ask_user.id, response.id])

def tether_offer_finilizer():
    pass