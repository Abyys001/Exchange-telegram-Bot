from pathlib import Path
from os import getcwd
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyromod import Client
from pyrogram import emoji, filters
import traceback
import logging

from .data import (
    admin_id, turn_all_offers_false, toman_form,
    able_offers, price_offers, get_state, CHANNEL_ID
)
from .offer_pic_generator import offer_draw
from .message_manager import message_manager

import sys
import types

# Patch the offer_pic_generator module if needed
if ".offer_pic_generator" in sys.modules:
    offer_pic_gen_mod = sys.modules[".offer_pic_generator"]
elif "plugins.offer_pic_generator" in sys.modules:
    offer_pic_gen_mod = sys.modules["plugins.offer_pic_generator"]
else:
    offer_pic_gen_mod = None

if offer_pic_gen_mod and not hasattr(offer_pic_gen_mod, "datetime"):
    import datetime as _real_datetime
    offer_pic_gen_mod.datetime = _real_datetime

# ============== SPECIAL OFFER HANDLER ==============

OFFER_LABELS = [
    "💳 خرید ویژه از حساب",
    "💵 خرید ویژه نقدی",
    "💲 خرید ویژه تتر",
    "💳 فروش ویژه از حساب",
    "💵 فروش ویژه نقدی",
    "💲 فروش ویژه تتر",
]
# نگاشت لیبل‌های با ایموجی به لیبل‌های اصلی بدون ایموجی (مطابق data.py)
OFFER_LABELS_MAP = {
    "💵 خرید ویژه نقدی": "خرید ویژه نقدی",
    "💳 خرید ویژه از حساب": "خرید ویژه از حساب",
    "💲 خرید ویژه تتر": "خرید ویژه تتر",
    "💵 فروش ویژه نقدی": "فروش ویژه نقدی",
    "💳 فروش ویژه از حساب": "فروش ویژه از حساب",
    "💲 فروش ویژه تتر": "فروش ویژه تتر",
}
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
    "<u>Office A\n"
    "708A High Road\n"
    "North Finchley\n"
    "N129QL<u/>\n\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n\n"
    "مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد\n\n"
    "⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید ⛔"
)

def get_offer_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(OFFER_LABELS[0], callback_data="offer_0"),
            InlineKeyboardButton(OFFER_LABELS[1], callback_data="offer_1")
        ],
        [
            InlineKeyboardButton(OFFER_LABELS[2], callback_data="offer_2"),
            InlineKeyboardButton(OFFER_LABELS[3], callback_data="offer_3")
        ],
        [InlineKeyboardButton(OFFER_LABELS[4], callback_data="offer_4")],
        [InlineKeyboardButton(OFFER_LABELS[5], callback_data="offer_5")],
        [InlineKeyboardButton(FINALIZE_LABEL, callback_data="offer_finalize")],
        [InlineKeyboardButton(BACK_LABEL, callback_data="offer_back")],
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(CANCEL_LABEL, callback_data="offer_cancel")]
    ])

def get_confirm_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(CONFIRM_LABEL, callback_data="offer_confirm"),
            InlineKeyboardButton(DECLINE_LABEL, callback_data="offer_decline")
        ]
    ])

async def special_offer(client, message, user_id=None, chat_id=None):
    """
    منوی خرید/فروش ویژه ادمین
    """
    try:
        keyboard = get_offer_keyboard()
        await client.send_message(
            message.chat.id,
            text="لطفاً نوع خرید یا فروش ویژه مورد نظر خود را انتخاب کنید:",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"[special_offer] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
            f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        )

# ============== Callback Handlers ==============

@Client.on_callback_query(filters.regex("^offer_0$"))  # 💳 خرید ویژه از حساب
async def offer_0_handler(client, callback_query):
    await callback_query.answer()
    await offer_handler(client, callback_query.message, OFFER_LABELS[0], callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_1$"))  # 💵 خرید ویژه نقدی
async def offer_1_handler(client, callback_query):
    await callback_query.answer()
    await offer_handler(client, callback_query.message, OFFER_LABELS[1], callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_2$"))  # 💲 خرید ویژه تتر
async def offer_2_handler(client, callback_query):
    await callback_query.answer()
    await offer_handler(client, callback_query.message, OFFER_LABELS[2], callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_3$"))  # 💳 فروش ویژه از حساب
async def offer_3_handler(client, callback_query):
    await callback_query.answer()
    await offer_handler(client, callback_query.message, OFFER_LABELS[3], callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_4$"))  # 💵 فروش ویژه نقدی
async def offer_4_handler(client, callback_query):
    await callback_query.answer()
    await offer_handler(client, callback_query.message, OFFER_LABELS[4], callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_5$"))  # 💲 فروش ویژه تتر
async def offer_5_handler(client, callback_query):
    await callback_query.answer()
    await offer_handler(client, callback_query.message, OFFER_LABELS[5], callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_finalize$"))
async def offer_finalize_handler(client, callback_query):
    await callback_query.answer()
    await offer_finalize(client, callback_query.message, callback_query.from_user.id, callback_query.message.chat.id)

@Client.on_callback_query(filters.regex("^offer_back$"))
async def offer_back_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # بازگشت به پنل ادمین
    from .admin_panel import admin_panel
    await admin_panel(client, callback_query.message, user_id, chat_id)

@Client.on_callback_query(filters.regex("^offer_cancel$"))
async def offer_cancel_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    turn_all_offers_false()
    
    # بازگشت به پنل ادمین
    from .admin_panel import admin_panel
    await admin_panel(client, callback_query.message, user_id, chat_id)

@Client.on_callback_query(filters.regex("^offer_confirm$"))
async def offer_confirm_handler(client, callback_query):
    await callback_query.answer()
    # این هندلر در offer_finalize استفاده می‌شود
    pass

@Client.on_callback_query(filters.regex("^offer_decline$"))
async def offer_decline_handler(client, callback_query):
    await callback_query.answer()
    # این هندلر در offer_finalize استفاده می‌شود
    pass

async def offer_handler(client, message, offer, user_id=None, chat_id=None):
    """
    ثبت قیمت برای یک پیشنهاد ویژه
    """
    try:
        await client.send_message(
            message.chat.id,
            text=f"💰 لطفاً قیمت {offer} را وارد کنید:",
            reply_markup=get_cancel_keyboard()
        )
        offer_price = await client.listen(message.chat.id)
        if not offer_price or not hasattr(offer_price, "text"):
            await message.reply("❗️ ورودی نامعتبر است. لطفاً مجدداً تلاش کنید.")
            return await offer_handler(client, message, offer, user_id=user_id, chat_id=chat_id)

        if offer_price.text == CANCEL_LABEL:
            turn_all_offers_false()
            
            # حذف پیام‌های قبلی و بازگشت به پنل ادمین
            if user_id and chat_id:
                await message_manager.cleanup_user_messages(client, user_id, chat_id)
                from .admin_panel import admin_panel
                await admin_panel(client, message, user_id, chat_id)
            else:
                await message.reply("⏪ عملیات لغو شد و به منوی اصلی بازگشتید.")
            return

        try:
            price = int(offer_price.text.replace(",", "").replace(" ", ""))
            if price <= 0:
                raise ValueError
        except Exception as e:
            await message.reply(
                f"❗️ لطفاً یک عدد معتبر وارد کنید.\n\n"
                f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
            )
            return await offer_handler(client, message, offer, user_id=user_id, chat_id=chat_id)

        turn_all_offers_false()
        # استفاده از نگاشت برای فعال‌سازی کلید صحیح
        offer_key = OFFER_LABELS_MAP.get(offer, offer)
        able_offers[offer_key] = True
        price_offers[offer_key] = price
        await message.reply(f"✅ قیمت {offer} با موفقیت به {toman_form(price)} تغییر یافت.")
        await special_offer(
            client,
            message,
            user_id or (getattr(message, "from_user", None) and message.from_user.id),
            chat_id or (getattr(message, "chat", None) and message.chat.id)
        )
    except Exception as e:
        logging.error(f"[offer_handler] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی در ثبت قیمت رخ داد. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
            f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        )

async def offer_finalize(client, message, user_id, chat_id):
    """
    نهایی کردن قیمت‌های ویژه و ارسال به کانال
    """
    try:
        try:
            # Patch: Ensure offer_pic_generator has correct datetime
            import sys
            import datetime as _real_datetime
            offer_pic_mod = None
            if ".offer_pic_generator" in sys.modules:
                offer_pic_mod = sys.modules[".offer_pic_generator"]
            elif "plugins.offer_pic_generator" in sys.modules:
                offer_pic_mod = sys.modules["plugins.offer_pic_generator"]
            if offer_pic_mod and not hasattr(offer_pic_mod, "datetime"):
                offer_pic_mod.datetime = _real_datetime

            state = get_state()
            if state is None:
                await message.reply("❌ هیچ آفر فعالی موجود نیست. لطفاً ابتدا یک آفر ویژه فعال کنید.")
                return
            
            offer_draw(state)
            image_path = Path(getcwd()) / f"./assets/offer{state}.png"
            await message.reply_photo(image_path, caption=MAIN_TEXT)
        except Exception as e:
            logging.error(f"[offer_finalize:draw] {e}\n{traceback.format_exc()}")
            await message.reply(
                f"⏳ لطفاً شکیبا باشید، در حال آماده‌سازی قیمت‌ها هستیم...\n\n"
                f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
            )
            return

        ask_msg = await client.send_message(
            admin_id[0],
            text="آیا از نهایی‌سازی قیمت‌های ویژه اطمینان دارید؟",
            reply_markup=get_confirm_keyboard()
        )

        # برای Inline Keyboard، باید از callback handler استفاده کنیم
        # این بخش نیاز به بازنویسی دارد

    except Exception as e:
        logging.error(f"[offer_finalize] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی در نهایی‌سازی قیمت‌ها رخ داد. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
            f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        )

# ============== Finalize Callback Handlers ==============

@Client.on_callback_query(filters.regex("^offer_confirm$"))
async def offer_finalize_confirm_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    try:
        # Patch: Ensure offer_pic_generator has correct datetime
        import sys
        import datetime as _real_datetime
        offer_pic_mod = None
        if ".offer_pic_generator" in sys.modules:
            offer_pic_mod = sys.modules[".offer_pic_generator"]
        elif "plugins.offer_pic_generator" in sys.modules:
            offer_pic_mod = sys.modules["plugins.offer_pic_generator"]
        if offer_pic_mod and not hasattr(offer_pic_mod, "datetime"):
            offer_pic_mod.datetime = _real_datetime

        state = get_state()
        if state is None:
            await message_manager.send_clean_message(
                client, chat_id, 
                "❌ هیچ آفر فعالی موجود نیست. لطفاً ابتدا یک آفر ویژه فعال کنید.",
                None, user_id
            )
            return
        
        offer_draw(state)
        image_path = Path(getcwd()) / f"./assets/offer{state}.png"
        await client.send_photo(CHANNEL_ID, image_path, caption=MAIN_TEXT)
        
        # ارسال پیام موفقیت و بازگشت به پنل ادمین
        success_message = f"🎉 قیمت‌های ویژه با موفقیت نهایی و به کانال ارسال شد {emoji.SPARKLES}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin")]
        ])
        
        await message_manager.send_clean_message(
            client, chat_id, success_message, keyboard, user_id
        )
        
    except Exception as e:
        logging.error(f"[offer_finalize:send_photo] {e}\n{traceback.format_exc()}")
        error_message = f"❌ خطا در ارسال به کانال. لطفاً بعداً تلاش کنید.\n\n🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin")]
        ])
        
        await message_manager.send_clean_message(
            client, chat_id, error_message, keyboard, user_id
        )

@Client.on_callback_query(filters.regex("^offer_decline$"))
async def offer_finalize_decline_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # بازگشت به پنل ادمین
    from .admin_panel import admin_panel
    await admin_panel(client, callback_query.message, user_id, chat_id)

# ================== TEST MODE ==================
if __name__ == "__main__":
    # حالت تستی: وقتی این فایل مستقیماً اجرا شود، همه قیمت‌ها را روی 128000 می‌گذارد و بنرها را تولید می‌کند
    import time

    # لیست کلیدهای آفر (بدون ایموجی)
    offer_keys = [
        "خرید ویژه نقدی",
        "خرید ویژه از حساب",
        "خرید ویژه تتر",
        "فروش ویژه نقدی",
        "فروش ویژه از حساب",
        "فروش ویژه تتر",
    ]
    # همه آفرها فعال و قیمت تستی
    for k in offer_keys:
        able_offers[k] = True
        price_offers[k] = 128000

    # تابع تستی برای تولید همه بنرها
    def test_generate_all_banners():
        for idx, k in enumerate(offer_keys, 1):
            try:
                # فرض بر این است که state همان ایندکس است (یا هر مقدار مورد نیاز offer_draw)
                offer_draw(idx)
                image_path = Path(getcwd()) / f"./assets/offer{idx}.png"
                if image_path.exists():
                    pass
                else:
                    pass
            except Exception as e:
                    pass
            time.sleep(0.5)
    test_generate_all_banners()
