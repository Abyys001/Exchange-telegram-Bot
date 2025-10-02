from pathlib import Path
from os import getcwd
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyromod import Client
from pyrogram import emoji, filters
import traceback
import logging
import asyncio

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
    "N129QL</u>\n\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n\n"
    "مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد\n\n"
    "⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید ⛔"
)

# متغیرهای مدیریت state
user_states = {}

def get_offer_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(OFFER_LABELS[0], callback_data="offer_0"),
            InlineKeyboardButton(OFFER_LABELS[1], callback_data="offer_1")
        ],
        [
            InlineKeyboardButton(OFFER_LABELS[4], callback_data="offer_4"),
            InlineKeyboardButton(OFFER_LABELS[3], callback_data="offer_3")
        ],
        [InlineKeyboardButton(OFFER_LABELS[2], callback_data="offer_2")],
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
        # حذف پیام‌های قبلی
        if user_id and chat_id:
            await message_manager.cleanup_user_messages(client, user_id, chat_id)
        
        keyboard = get_offer_keyboard()
        msg = await client.send_message(
            message.chat.id,
            text="👋 به منوی خرید/فروش ویژه خوش آمدید!\n\nلطفاً نوع خرید یا فروش ویژه مورد نظر خود را انتخاب کنید:",
            reply_markup=keyboard
        )
        
        # ذخیره پیام برای مدیریت بعدی
 
    except Exception as e:
        logging.error(f"[special_offer] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید.\n\n"
            f"🔎 جزییات خطا: {str(e)}"
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

async def offer_handler(client, message, offer, user_id=None, chat_id=None):
    """
    ثبت قیمت برای یک پیشنهاد ویژه
    """
    try:
        # حذف پیام‌های قبلی
        if user_id and chat_id:
            await message_manager.cleanup_user_messages(client, user_id, chat_id)
        
        msg = await client.send_message(
            message.chat.id,
            text=f"💰 لطفاً قیمت {offer} را به عدد وارد کنید:",
            reply_markup=get_cancel_keyboard()
        )
        
        
        # ذخیره state کاربر
        user_states[user_id] = {"waiting_for_price": offer}
        
        # انتظار برای دریافت قیمت
        offer_price = await client.listen(message.chat.id)
        
        if not offer_price or not hasattr(offer_price, "text"):
            await message.reply("⏰ زمان دریافت قیمت به پایان رسید. لطفاً مجدداً تلاش کنید.")
            return await special_offer(client, message, user_id, chat_id)

        if offer_price.text == CANCEL_LABEL:
            turn_all_offers_false()
            await message.reply("⏪ عملیات لغو شد.")
            return await special_offer(client, message, user_id, chat_id)

        try:
            price = int(offer_price.text.replace(",", "").replace(" ", "").replace("تومان", "").strip())
            if price <= 0:
                raise ValueError("قیمت باید بزرگتر از صفر باشد")
        except Exception as e:
            error_msg = await client.send_message(
                message.chat.id,
                text=f"❗️ لطفاً یک عدد معتبر وارد کنید. مثال: 58000 یا 58,000"
            )
            await asyncio.sleep(2)
            return await offer_handler(client, message, offer, user_id, chat_id)

        # ثبت قیمت
        turn_all_offers_false()
        offer_key = OFFER_LABELS_MAP.get(offer, offer)
        able_offers[offer_key] = True
        price_offers[offer_key] = price
        
        success_msg = await client.send_message(
            message.chat.id,
            text=f"✅ قیمت {offer} با موفقیت به {toman_form(price)} تغییر یافت."
        )
        
        await asyncio.sleep(1)
        await special_offer(client, message, user_id, chat_id)
        
    except asyncio.TimeoutError:
        await message.reply("⏰ زمان دریافت قیمت به پایان رسید. لطفاً مجدداً تلاش کنید.")
        await special_offer(client, message, user_id, chat_id)
    except Exception as e:
        logging.error(f"[offer_handler] {e}\n{traceback.format_exc()}")
        await message.reply(f"❌ خطایی در ثبت قیمت رخ داد: {str(e)}")

async def offer_finalize(client, message, user_id, chat_id):
    """
    نهایی کردن قیمت‌های ویژه و ارسال به کانال
    """
    try:
        # حذف پیام‌های قبلی
        await message_manager.cleanup_user_messages(client, user_id, chat_id)
        
        # بررسی آیا حداقل یک آفر فعال وجود دارد
        active_offers = any(able_offers.values())
        if not active_offers:
            error_msg = await client.send_message(
                chat_id,
                text="❌ هیچ آفر فعالی موجود نیست. لطفاً ابتدا حداقل یک آفر ویژه را تنظیم کنید."
            )
            await asyncio.sleep(2)
            return await special_offer(client, message, user_id, chat_id)
        
        # تولید عکس
        try:
            state = get_state()
            if state is None:
                state = 1  # حالت پیش‌فرض
            
            offer_draw(state)
            image_path = Path(getcwd()) / f"./assets/offer{state}.png"
            
            if not image_path.exists():
                raise FileNotFoundError(f"عکس تولید شده یافت نشد: {image_path}")
                
            # نمایش پیش‌نمایش به ادمین
            preview_msg = await client.send_photo(
                chat_id,
                photo=image_path,
                caption="📋 پیش‌نمایش قیمت‌های ویژه:\n\n" + MAIN_TEXT
            )
            
        except Exception as e:
            logging.error(f"[offer_finalize:draw] {e}\n{traceback.format_exc()}")
            error_msg = await client.send_message(
                chat_id,
                text=f"❌ خطا در تولید عکس: {str(e)}\n\nلطفاً از پشتیبانی کمک بگیرید."
            )
            return
        
        # درخواست تأیید نهایی‌سازی
        confirm_msg = await client.send_message(
            chat_id,
            text="❓ آیا از نهایی‌سازی قیمت‌های ویژه و ارسال به کانال اطمینان دارید؟",
            reply_markup=get_confirm_keyboard()
        )
        
        # ذخیره state برای هندلرهای تأیید
        user_states[user_id] = {"finalizing": True, "image_path": image_path}
        
    except Exception as e:
        logging.error(f"[offer_finalize] {e}\n{traceback.format_exc()}")
        await message.reply(f"❌ خطایی در نهایی‌سازی رخ داد: {str(e)}")

# ============== Finalize Callback Handlers ==============

@Client.on_callback_query(filters.regex("^offer_confirm$"))
async def offer_confirm_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    try:
        # حذف پیام‌های قبلی
        await message_manager.cleanup_user_messages(client, user_id, chat_id)
        
        # بررسی state کاربر
        user_state = user_states.get(user_id, {})
        image_path = user_state.get("image_path")
        
        if not image_path or not Path(image_path).exists():
            error_msg = await client.send_message(
                chat_id,
                text="❌ عکس قیمت‌ها یافت نشد. لطفاً مجدداً تلاش کنید."
            )
            return await special_offer(client, callback_query.message, user_id, chat_id)
        
        # ارسال به کانال
        try:
            await client.send_photo(
                CHANNEL_ID,
                photo=image_path,
                caption=MAIN_TEXT
            )
            
            success_msg = await client.send_message(
                chat_id,
                text="🎉 قیمت‌های ویژه با موفقیت نهایی و به کانال ارسال شد! " + emoji.SPARKLES
            )
            
        except Exception as e:
            logging.error(f"[offer_confirm:send_to_channel] {e}\n{traceback.format_exc()}")
            error_msg = await client.send_message(
                chat_id,
                text=f"❌ خطا در ارسال به کانال: {str(e)}"
            )
        
        # بازگشت به منوی اصلی بعد از 3 ثانیه
        await asyncio.sleep(3)
        from .admin_panel import admin_panel
        await admin_panel(client, callback_query.message, user_id, chat_id)
        
    except Exception as e:
        logging.error(f"[offer_confirm_handler] {e}\n{traceback.format_exc()}")
        await callback_query.message.reply(f"❌ خطایی رخ داد: {str(e)}")

@Client.on_callback_query(filters.regex("^offer_decline$"))
async def offer_decline_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    msg = await client.send_message(
        chat_id,
        text="🔄 به منوی خرید/فروش ویژه بازگشتید."
    )

    
    await asyncio.sleep(1)
    await special_offer(client, callback_query.message, user_id, chat_id)

# پاک کردن stateهای قدیمی
async def cleanup_old_states():
    while True:
        await asyncio.sleep(30)  # هر 5 دقیقه
        current_time = asyncio.get_event_loop().time()
        for user_id in list(user_states.keys()):
            # اگر state بیش از 10 دقیقه قدیمی باشد، پاک شود
            if user_states[user_id].get("timestamp", 0) + 600 < current_time:
                del user_states[user_id]

# اجرای تمیزکننده stateها
async def start_cleanup_task():
    asyncio.create_task(cleanup_old_states())