from pathlib import Path
from os import getcwd
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram import filters
from pyromod import Client
from .offer_pic_generator import create_image_for_tether_offer
from .data import toman_form, tether_price, admin_id, CHANNEL_ID
from .message_manager import message_manager, get_back_button

STOP_KEY = "↩️ بازگشت"

FINAL_MESSAGE = (
    "💷 خرید فروش تتر و پوند نقدی و حسابی\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "Mr. Mahdi    📞  +447533544249\n\n"
    "Ms. Kianian    📞  +989121894230\n\n"
    "Manager  📞  +447399990340\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "📌آدرس دفتر :\n"
    "<u>Office A\n"
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
        InlineKeyboardButton("کانال تلگرام ما", url="https://t.me/sarafipardis"),
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

def get_inline_keyboard(buttons, callback_prefix=""):
    """
    ساخت کیبورد اینلاین با دکمه‌های داده شده
    """
    keyboard_buttons = []
    for i, row in enumerate(buttons):
        row_buttons = []
        for j, text in enumerate(row if isinstance(row, list) else [row]):
            callback_data = f"{callback_prefix}_{i}_{j}" if callback_prefix else f"tether_{i}_{j}"
            row_buttons.append(InlineKeyboardButton(text, callback_data=callback_data))
        keyboard_buttons.append(row_buttons)
    return InlineKeyboardMarkup(keyboard_buttons)

async def tether_price_menu(client, message):
    """
    منوی انتخاب نوع قیمت تتر
    """
    user_id = message.from_user.id if hasattr(message, 'from_user') else None
    chat_id = message.chat.id
    
    keyboard = get_inline_keyboard(TETHER_BUTTONS + [[STOP_KEY]], "tether_price")
    keyboard.inline_keyboard.append([get_back_button("back_to_admin", "🔙 بازگشت به پنل ادمین")])
    
    if user_id:
        await message_manager.send_clean_message(
            client, chat_id,
            "لطفاً نوع قیمت تتر مورد نظر خود را انتخاب کنید 👇",
            keyboard, user_id
        )
    else:
        await message.reply(
            "لطفاً نوع قیمت تتر مورد نظر خود را انتخاب کنید 👇",
            reply_markup=keyboard
        )

# ============== Callback Handlers ==============

@Client.on_callback_query(filters.regex("^tether_price_0_0$"))  # 🟢 خرید تتر ریال
async def tether_buy_irr_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, tether_form="tether_buy_irr")

@Client.on_callback_query(filters.regex("^tether_price_0_1$"))  # 🔴 فروش تتر ریال
async def tether_sell_irr_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, tether_form="tether_sell_irr")

@Client.on_callback_query(filters.regex("^tether_price_1_0$"))  # 🟢 خرید تتر پوند
async def tether_buy_gbp_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, tether_form="tether_buy_gbp")

@Client.on_callback_query(filters.regex("^tether_price_1_1$"))  # 🔴 فروش تتر پوند
async def tether_sell_gbp_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await ask_price_value(client, callback_query.message, tether_form="tether_sell_gbp")

@Client.on_callback_query(filters.regex("^tether_price_2_0$"))  # ↩️ بازگشت
async def tether_back_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await tether_main_menu(client, callback_query.message)

async def tether_main_menu(client, message):
    """
    منوی اصلی تنظیمات تتر
    """
    user_id = message.from_user.id if hasattr(message, 'from_user') else None
    chat_id = message.chat.id
    
    keyboard = get_inline_keyboard([[action] for action in MAIN_MENU_ACTIONS], "tether_main")
    keyboard.inline_keyboard.append([get_back_button("back_to_admin", "🔙 بازگشت به پنل ادمین")])
    
    if user_id:
        await message_manager.send_clean_message(
            client, chat_id,
            "👋 به منوی مدیریت قیمت‌های تتر خوش آمدید!\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            keyboard, user_id
        )
    else:
        await message.reply(
            "👋 به منوی مدیریت قیمت‌های تتر خوش آمدید!\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=keyboard
        )

# ============== Main Menu Callback Handlers ==============

@Client.on_callback_query(filters.regex("^tether_main_0_0$"))  # 📝 تنظیم قیمت‌ها
async def tether_set_prices_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await tether_price_menu(client, callback_query.message)

@Client.on_callback_query(filters.regex("^tether_main_1_0$"))  # ✅ نهایی‌سازی
async def tether_finalize_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await tether_final(client, callback_query.message)

@Client.on_callback_query(filters.regex("^tether_main_2_0$"))  # ↩️ بازگشت
async def tether_main_back_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    return

async def ask_price_value(client, message, tether_form):
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
        return await tether_price_menu(client, message)

    text = response.text.strip()

    if text == STOP_KEY:
        return await tether_price_menu(client, message)

    try:
        value = float(text)
        formatted_price = toman_form(int(value)) if value.is_integer() else str(value)
        tether_price[tether_form] = formatted_price
        await client.send_message(chat_id, f"✅ قیمت با موفقیت ذخیره شد: {formatted_price}")
    except:
        await client.send_message(chat_id, "⚠️ لطفاً فقط عدد صحیح وارد کنید.")
    
    await tether_price_menu(client, message)

async def tether_final(client, message):
    """
    ارسال عکس و پیام نهایی به ادمین و کانال
    """
    try:
        image_path = Path(getcwd()) / create_image_for_tether_offer()
        await message.reply_photo(image_path, caption=FINAL_MESSAGE, reply_markup=FINAL_KEYBOARD)
    except Exception as e:
        print(f"[tether_final] Error sending photo: {e}")
        await message.reply("⛔️ خطا در ارسال عکس و پیام نهایی.")
        return

    keyboard = get_inline_keyboard([FINAL_CONFIRM_ACTIONS], "tether_final")
    await message.reply(
        "آیا از نهایی‌سازی و ارسال قیمت‌ها به کانال اطمینان دارید؟\n\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=keyboard
    )

# ============== Final Confirmation Callback Handlers ==============

@Client.on_callback_query(filters.regex("^tether_final_0_0$"))  # ✅ بله
async def tether_final_confirm_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await message_manager.send_clean_message(
        client, chat_id, "⏳ در حال نهایی‌سازی و ارسال به کانال...", None, user_id
    )
    
    try:
        image_path = Path(getcwd()) / create_image_for_tether_offer()
        await client.send_photo(CHANNEL_ID, image_path, caption=FINAL_MESSAGE, reply_markup=FINAL_KEYBOARD)
    except Exception as e:
        print(f"[tether_final_confirm_handler] Error sending photo to channel: {e}")
        error_text = f"⛔️ خطا در ارسال به کانال: {str(e)}"
        await message_manager.send_clean_message(
            client, chat_id, error_text, None, user_id
        )
        return
    
    # ارسال پیام موفقیت و بازگشت به پنل ادمین
    success_message = "✅ نهایی‌سازی با موفقیت انجام شد و قیمت‌ها به کانال ارسال گردید!"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت به پنل ادمین", callback_data="back_to_admin")]
    ])
    
    await message_manager.send_clean_message(
        client, chat_id, success_message, keyboard, user_id
    )

@Client.on_callback_query(filters.regex("^tether_final_0_1$"))  # ❌ خیر
async def tether_final_decline_handler(client, callback_query):
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
        print(f"[tether_final_decline_handler] Error returning to admin panel: {e}")
        await client.send_message(chat_id, text=f"⛔️ خطا در بازگشت به پنل ادمین: {str(e)}")

