from pathlib import Path
from os import getcwd
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)
from pyromod import Client
from pyrogram import filters
from .data import send_data, CHANNEL_ID, admin_id, get_state, turn_all_calls_false
from pyrogram import emoji
from .pic_generator import draw
from .offer_pic_generator import offer_draw
from .message_manager import message_manager

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
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ بله، نهایی کن", callback_data="finalize_confirm"),
            InlineKeyboardButton("🔄 خیر، نیاز به تغییر دارم", callback_data="finalize_decline")
        ]
    ])

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
    return ask_user

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

    ask_user = await _get_admin_confirmation(
        client, id_of_chat, chat_id, "آیا از نهایی کردن قیمت‌ها اطمینان دارید؟"
    )

# ============== Finalize Callback Handlers ==============

@Client.on_callback_query(filters.regex("^finalize_confirm$"))
async def finalize_confirm_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    send_data()
    draw()
    data_folder = Path(getcwd())
    image_path = data_folder / "assets/prices.png"
    
    await _send_image_with_caption(
        lambda img, **kwargs: client.send_photo(CHANNEL_ID, img, **kwargs),
        image_path
    )
    
    # ارسال پیام موفقیت و بازگشت به پنل ادمین
    success_message = f"✅ قیمت‌ها با موفقیت نهایی شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}\n\nدر صورت نیاز به تغییر، می‌توانید مجدداً اقدام کنید."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin")]
    ])
    
    await message_manager.send_clean_message(
        client, chat_id, success_message, keyboard, user_id
    )
    
    turn_all_calls_false()

@Client.on_callback_query(filters.regex("^finalize_decline$"))
async def finalize_decline_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # بازگشت به پنل ادمین
    from .admin_panel import admin_panel
    await admin_panel(client, callback_query.message, user_id, chat_id)

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

    ask_user = await _get_admin_confirmation(
        client, id_of_chat, chat_id, "آیا از نهایی کردن قیمت‌های ویژه اطمینان دارید؟"
    )

# ============== Special Offers Finalize Callback Handlers ==============

@Client.on_callback_query(filters.regex("^finalize_special_confirm$"))
async def finalize_special_confirm_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    state = get_state()
    data_folder = Path(getcwd())
    image_path = data_folder / f"assets/offer{state}.png"
    
    offer_draw(state)
    await _send_image_with_caption(
        lambda img, **kwargs: client.send_photo(CHANNEL_ID, img, **kwargs),
        image_path
    )
    
    # ارسال پیام موفقیت و بازگشت به پنل ادمین
    success_message = f"🎉 قیمت‌های ویژه با موفقیت نهایی شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}\n\nدر صورت نیاز به تغییر، می‌توانید مجدداً اقدام کنید."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin")]
    ])
    
    await message_manager.send_clean_message(
        client, chat_id, success_message, keyboard, user_id
    )

@Client.on_callback_query(filters.regex("^finalize_special_decline$"))
async def finalize_special_decline_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # بازگشت به پنل ادمین
    from .admin_panel import admin_panel
    await admin_panel(client, callback_query.message, user_id, chat_id)

def tether_offer_finilizer():
    pass