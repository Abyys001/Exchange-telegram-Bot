from pathlib import Path
from os import getcwd
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from pyromod import Client
from pyrogram import filters

from .data import *
from .pic_generator import draw
from .message_manager import message_manager, get_back_button
import aiohttp
import asyncio
import logging

# ============== API CONFIGURATION ==============
API_URL = "https://pardis.cybercina.co.uk/wp-json/pardis/v1/rates"
API_KEY = "PX9k7mN2qR8vL4jH6wE3tY1uI5oP0aS9dF7gK2mN8xZ4cV6bQ1wE3rT5yU8iO0pL"

STOP_KEY = "↩️ بازگشت"

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
N129QL</u>

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

POUND_BUTTONS = [
    ["🔴 فروش پوند تومن", "🟢 خرید پوند تومن"],
    ["🔴 فروش پوند پوند", "🟢 خرید پوند پوند"]
]

POUND_BUTTONS_TRANSLATE = {
    "🟢 خرید پوند تومن": "pound_buy_irr",
    "🔴 فروش پوند تومن": "pound_sell_irr",
    "🟢 خرید پوند پوند": "pound_buy_gbp",
    "🔴 فروش پوند پوند": "pound_sell_gbp"
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

# تعریف مسیر و نام فایل عکس
IMAGE_FILENAME = "prices.png"
IMAGE_PATH = Path(getcwd()) / "assets" / IMAGE_FILENAME

def get_inline_keyboard(buttons, callback_prefix=""):
    """
    ساخت کیبورد اینلاین با دکمه‌های داده شده
    """
    keyboard_buttons = []
    for i, row in enumerate(buttons):
        row_buttons = []
        for j, text in enumerate(row if isinstance(row, list) else [row]):
            callback_data = f"{callback_prefix}_{i}_{j}" if callback_prefix else f"pound_{i}_{j}"
            row_buttons.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard_buttons.append(row_buttons)
    return InlineKeyboardMarkup(keyboard_buttons)

async def update_currency_rate(currency_type, rate_value):
    """
    تابع برای به‌روزرسانی قیمت از طریق API
    """
    try:
        # تبدیل قیمت از فرمت تومان به عدد
        if isinstance(rate_value, str):
            # حذف کاما و تبدیل به عدد
            clean_rate = rate_value.replace(',', '').replace('تومان', '').strip()
            rate_num = int(clean_rate)
        else:
            rate_num = int(rate_value)
        
        data = {
            "currency": currency_type,
            "rate": rate_num,
            "api_key": API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=data) as response:
                result = await response.json()
                return result.get('success', False), result
                
    except Exception as e:
        logging.error(f"Error updating {currency_type}: {e}")
        return False, str(e)

async def update_all_rates():
    """
    به‌روزرسانی همه قیمت‌های پوند در API
    """
    results = {}
    
    # مپ کردن قیمت‌های داخلی به currencyهای API (ساختار جدید)
    rate_mapping = {
        "pound_buy_irr": "GBP",  # فقط GBP برای پوند
        "pound_sell_irr": "GBP", # فقط GBP برای پوند
    }
    
    for internal_key, api_currency in rate_mapping.items():
        if internal_key in pound_price and pound_price[internal_key]:
            success, result = await update_currency_rate(api_currency, pound_price[internal_key])
            results[api_currency] = {
                "success": success,
                "result": result,
                "rate": pound_price[internal_key]
            }
            await asyncio.sleep(0.5)
    
    return results

async def pound_price_menu(client, message):
    """
    منوی انتخاب نوع قیمت پوند
    """
    user_id = message.from_user.id if hasattr(message, 'from_user') else None
    chat_id = message.chat.id
    
    keyboard = get_inline_keyboard(POUND_BUTTONS + [[STOP_KEY]], "pound_price")
    keyboard.inline_keyboard.append([get_back_button("back_to_admin", "🔙 بازگشت به پنل ادمین")])
    
    if user_id:
        await message_manager.send_clean_message(
            client, chat_id,
            "لطفاً نوع قیمت پوند مورد نظر خود را انتخاب کنید 👇",
            keyboard, user_id
        )
    else:
        await message.reply(
            "لطفاً نوع قیمت پوند مورد نظر خود را انتخاب کنید 👇",
            reply_markup=keyboard
        )

# ============== Callback Handlers ==============

@Client.on_callback_query(filters.regex("^pound_price_0_1$"))  # 🟢 خرید پوند تومن
async def pound_buy_irr_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, pound_form="pound_buy_irr")

@Client.on_callback_query(filters.regex("^pound_price_0_0$"))  # 🔴 فروش پوند تومن
async def pound_sell_irr_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, pound_form="pound_sell_irr")

@Client.on_callback_query(filters.regex("^pound_price_1_1$"))  # 🟢 خرید پوند پوند
async def pound_buy_gbp_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, pound_form="pound_buy_gbp")

@Client.on_callback_query(filters.regex("^pound_price_1_0$"))  # 🔴 فروش پوند پوند
async def pound_sell_gbp_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, pound_form="pound_sell_gbp")

@Client.on_callback_query(filters.regex("^pound_price_2_0$"))  # ↩️ بازگشت
async def pound_back_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await pound_main_menu(client, callback_query.message)

async def pound_main_menu(client, message):
    """
    منوی اصلی تنظیمات پوند
    """
    user_id = message.from_user.id if hasattr(message, 'from_user') else None
    chat_id = message.chat.id
    
    keyboard = get_inline_keyboard([[action] for action in MAIN_MENU_ACTIONS], "pound_main")
    keyboard.inline_keyboard.append([get_back_button("back_to_admin", "🔙 بازگشت به پنل ادمین")])
    
    if user_id:
        await message_manager.send_clean_message(
            client, chat_id,
            "👋 به منوی مدیریت قیمت‌های پوند خوش آمدید!\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            keyboard, user_id
        )
    else:
        await message.reply(
            "👋 به منوی مدیریت قیمت‌های پوند خوش آمدید!\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboard
        )

# ============== Main Menu Callback Handlers ==============

@Client.on_callback_query(filters.regex("^pound_main_0_0$"))  # 📝 تنظیم قیمت‌ها
async def pound_set_prices_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await pound_price_menu(client, callback_query.message)

@Client.on_callback_query(filters.regex("^pound_main_1_0$"))  # ✅ نهایی‌سازی
async def pound_finalize_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await pound_final(client, callback_query.message)

@Client.on_callback_query(filters.regex("^pound_main_2_0$"))  # ↩️ بازگشت
async def pound_main_back_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    return

async def ask_price_value(client, message, pound_form):
    """
    دریافت مقدار قیمت از ادمین و ثبت آن
    """
    user_id = message.from_user.id
    chat_id = message.chat.id

    await message.reply("لطفاً مقدار قیمت مورد نظر را به عدد وارد کنید (مثال: ۵۸۵۰۰):")
    
    # صبر میکنیم پیام بعدی کاربر در همین چت
    response = await client.listen(chat_id=chat_id)

    if not response or not response.text:
        await client.send_message(chat_id, "❗ ورودی نامعتبر است.")
        return await pound_price_menu(client, message)

    text = response.text.strip()

    if text == STOP_KEY:
        return await pound_price_menu(client, message)

    try:
        value = float(text)
        formatted_price = toman_form(int(value)) if value.is_integer() else str(value)
        pound_price[pound_form] = formatted_price
        await client.send_message(chat_id, f"✅ قیمت با موفقیت ذخیره شد: {formatted_price}")
    except:
        await client.send_message(chat_id, "⚠️ لطفاً فقط عدد صحیح وارد کنید.")
    
    await pound_price_menu(client, message)

async def pound_final(client, message):
    """
    ارسال عکس و پیام نهایی به ادمین و کانال
    """
    try:
        # ایجاد عکس
        draw()
        
        # بررسی وجود فایل
        if not IMAGE_PATH.exists():
            raise FileNotFoundError(f"Image file not found: {IMAGE_PATH}")
        
        await message.reply_photo(IMAGE_PATH, caption=FINAL_MESSAGE, reply_markup=FINAL_KEYBOARD)
    except Exception as e:
        logging.error(f"[pound_final] Error sending photo: {e}")
        await message.reply("⛔️ خطا در ارسال عکس و پیام نهایی.")
        return

    keyboard = get_inline_keyboard([FINAL_CONFIRM_ACTIONS], "pound_final")
    await message.reply(
        "آیا از نهایی‌سازی و ارسال قیمت‌ها به کانال اطمینان دارید؟\n\n"
        "⚠️ توجه: با تایید، قیمت‌های زیر در وب‌سایت نیز به‌روزرسانی خواهند شد:\n"
        f"•  خرید پوند: {prices.get('buy_from_account', 'تعیین نشده')}\n"
        f"•  فروش پوند: {prices.get('sell_from_account', 'تعیین نشده')}\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )

# ============== Final Confirmation Callback Handlers ==============

@Client.on_callback_query(filters.regex("^pound_final_0_0$"))  # ✅ بله
async def pound_final_confirm_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await message_manager.send_clean_message(
        client, chat_id, "⏳ در حال نهایی‌سازی و ارسال به کانال...", None, user_id
    )
    
    # ابتدا همه قیمت‌ها را در API به‌روزرسانی می‌کنیم
    update_results = await update_all_rates()
    
    # بررسی نتایج به‌روزرسانی
    failed_updates = []
    for currency, result in update_results.items():
        if not result["success"]:
            failed_updates.append(f"{currency}: {result.get('result', 'خطا')}")
    
    # ارسال عکس به کانال
    try:
        # ایجاد عکس مجدد برای اطمینان از به روز بودن
        draw()
        
        # بررسی وجود فایل
        if not IMAGE_PATH.exists():
            raise FileNotFoundError(f"Image file not found: {IMAGE_PATH}")
        

        buy_price = safe_int(prices.get("buy_from_account"))
        sell_price = safe_int(prices.get("sell_from_account"))

        if buy_price != 0:
            send_gbp_buy(buy_price)

        if sell_price != 0:
            send_gbp_sell(sell_price)


        await client.send_photo(CHANNEL_ID, IMAGE_PATH, caption=FINAL_MESSAGE, reply_markup=FINAL_KEYBOARD)
        
        # آماده کردن پیام نتیجه
        if failed_updates:
            success_message = (
                "✅ نهایی‌سازی با موفقیت انجام شد و قیمت‌ها به کانال ارسال گردید!\n\n"
                f"⚠️ برخی قیمت‌ها در وب‌سایت به‌روزرسانی نشدند:\n"
                f"{chr(10).join(failed_updates)}"
            )
        else:
            success_message = (
                "✅ نهایی‌سازی با موفقیت انجام شد!\n\n"
                "• قیمت‌ها به کانال ارسال گردید\n"
                "• همه قیمت‌ها در وب‌سایت به‌روزرسانی شدند"
            )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin")]
        ])
        
        await message_manager.send_clean_message(
            client, chat_id, success_message, keyboard, user_id
        )
        
    except Exception as e:
        logging.error(f"[pound_final_confirm_handler] Error sending photo to channel: {e}")
        error_text = f"⛔️ خطا در ارسال به کانال: {str(e)}"
        await message_manager.send_clean_message(
            client, chat_id, error_text, None, user_id
        )

@Client.on_callback_query(filters.regex("^pound_final_0_1$"))  # ❌ خیر
async def pound_final_decline_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # بازگشت به پنل ادمین
    try:
        from .admin_panel import admin_panel
        await admin_panel(client, callback_query.message, user_id, chat_id)
    except Exception as e:
        logging.error(f"[pound_final_decline_handler] Error returning to admin panel: {e}")
        await client.send_message(chat_id, text=f"⛔️ خطا در بازگشت به پنل ادمین: {str(e)}")

# ============== Entry Point ==============

async def pound_offer_finilizer(client, message):
    """
    نقطه ورود برای مدیریت قیمت‌های پوند
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await pound_main_menu(client, message)