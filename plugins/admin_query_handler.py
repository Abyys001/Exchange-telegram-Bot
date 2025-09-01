from pyromod import Client
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .data import prices, able, toman_form, add_price_to_call
from .admin_panel import admin_panel  # type: ignore

# ============== Constants ==============
STOP_BUY = "⛔️ توقف این حالت از خرید"
STOP_SELL = "⛔️ توقف این حالت از فروش"
MAKE_CALL = "📞 تماس بگیرید"

BUY_FORMS = [
    "💳 خرید از حساب",
    "💵 خرید نقدی",
    "⛔️ توقف همه خریدها",
    "🔙 بازگشت به منوی اصلی",
]

SELL_FORMS = [
    "💳 فروش از حساب",
    "💵 فروش نقدی",
    "🏦 رسمی",
    "⛔️توقف همه فروش‌ها",
    "🔙 بازگشت به منوی اصلی",
]

def get_stop_keyboard(stop_text):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(MAKE_CALL, callback_data="make_call")],
        [InlineKeyboardButton(stop_text, callback_data="stop_action")]
    ])

STOP_BUY_KEYBOARD = get_stop_keyboard(STOP_BUY)
STOP_SELL_KEYBOARD = get_stop_keyboard(STOP_SELL)

# ============== Main Buy/Sell Handlers ==============

def get_buy_action_map():
    return {
        BUY_FORMS[0]: change_buy_from_account_price,
        BUY_FORMS[1]: change_cash_purchase_price,
        BUY_FORMS[2]: stop_buy,
        BUY_FORMS[3]: lambda c, q: admin_panel(c, q.message, q.message.chat.id, q.from_user.id),
    }

def get_sell_action_map():
    return {
        SELL_FORMS[0]: change_sell_from_account_price,
        SELL_FORMS[1]: cash_sell,
        SELL_FORMS[2]: change_official_sell_price,
        SELL_FORMS[3]: stop_sell,
        SELL_FORMS[4]: lambda c, q: admin_panel(c, q.message, q.message.chat.id, q.from_user.id),
    }

def get_buy_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(BUY_FORMS[0], callback_data="buy_from_account"),
            InlineKeyboardButton(BUY_FORMS[1], callback_data="cash_purchase")
        ],
        [InlineKeyboardButton(BUY_FORMS[2], callback_data="stop_all_buy")],
        [InlineKeyboardButton(BUY_FORMS[3], callback_data="back_to_main_menu")]
    ])

def get_sell_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(SELL_FORMS[0], callback_data="sell_from_account"),
            InlineKeyboardButton(SELL_FORMS[1], callback_data="cash_sell")
        ],
        [
            InlineKeyboardButton(SELL_FORMS[2], callback_data="official_sell"),
            InlineKeyboardButton(SELL_FORMS[3], callback_data="stop_all_sell")
        ],
        [InlineKeyboardButton(SELL_FORMS[4], callback_data="back_to_main_menu")],
    ])

@Client.on_callback_query(filters.regex(r"^buy$"))
async def change_buy_price(client, callback_query):
    await callback_query.answer()
    chat_id = callback_query.message.chat.id
    await client.send_message(
        chat_id,
        "🛒 لطفاً نوع خریدی که می‌خواهید تغییر دهید را انتخاب کنید:",
        reply_markup=get_buy_keyboard()
    )

@Client.on_callback_query(filters.regex(r"^sell$"))
async def sell_price(client, callback_query):
    await callback_query.answer()
    chat_id = callback_query.message.chat.id
    await client.send_message(
        chat_id,
        "💰 لطفاً نوع فروشی که می‌خواهید تغییر دهید را انتخاب کنید:",
        reply_markup=get_sell_keyboard()
    )

# ============== Buy/Sell Callback Handlers ==============

@Client.on_callback_query(filters.regex(r"^buy_from_account$"))
async def buy_from_account_handler(client, callback_query):
    await callback_query.answer()
    await change_buy_from_account_price(client, callback_query)

@Client.on_callback_query(filters.regex(r"^cash_purchase$"))
async def cash_purchase_handler(client, callback_query):
    await callback_query.answer()
    await change_cash_purchase_price(client, callback_query)

@Client.on_callback_query(filters.regex(r"^stop_all_buy$"))
async def stop_all_buy_handler(client, callback_query):
    await callback_query.answer()
    await stop_buy(client, callback_query)

@Client.on_callback_query(filters.regex(r"^sell_from_account$"))
async def sell_from_account_handler(client, callback_query):
    await callback_query.answer()
    await change_sell_from_account_price(client, callback_query)

@Client.on_callback_query(filters.regex(r"^cash_sell$"))
async def cash_sell_handler(client, callback_query):
    await callback_query.answer()
    await cash_sell(client, callback_query)

@Client.on_callback_query(filters.regex(r"^official_sell$"))
async def official_sell_handler(client, callback_query):
    await callback_query.answer()
    await change_official_sell_price(client, callback_query)

@Client.on_callback_query(filters.regex(r"^stop_all_sell$"))
async def stop_all_sell_handler(client, callback_query):
    await callback_query.answer()
    await stop_sell(client, callback_query)

@Client.on_callback_query(filters.regex(r"^make_call$"))
async def make_call_handler(client, callback_query):
    await callback_query.answer()
    chat_id = callback_query.message.chat.id
    add_price_to_call("current_able_key")  # این باید بر اساس context تنظیم شود
    await client.send_message(chat_id, "📞 درخواست تماس شما با موفقیت ثبت شد. لطفاً منتظر تماس باشید.")

@Client.on_callback_query(filters.regex(r"^stop_action$"))
async def stop_action_handler(client, callback_query):
    await callback_query.answer()
    # این باید بر اساس context تنظیم شود
    await client.send_message(callback_query.message.chat.id, "⛔️ عملیات متوقف شد.")

# ============== Change Price Functions ==============

async def change_sell_from_account_price(client, query):
    await handle_price_change(
        client, query,
        price_key="sell_from_account",
        able_key="sell_from_account",
        stop_text=STOP_SELL,
        stop_keyboard=STOP_SELL_KEYBOARD,
        success_message="✅ قیمت جدید فروش از حساب شما: {price} تومان ثبت شد.",
        stop_message="⛔️ فروش از حساب شما غیرفعال شد.",
        back_func=sell_price,
    )

async def cash_sell(client, query):
    await handle_price_change(
        client, query,
        price_key="cash_sales_price",
        able_key="cash_sales_price",
        stop_text=STOP_SELL,
        stop_keyboard=STOP_SELL_KEYBOARD,
        success_message="✅ قیمت جدید فروش نقدی شما: {price} تومان ثبت شد.",
        stop_message="⛔️ فروش نقدی شما غیرفعال شد.",
        back_func=sell_price,
    )

async def change_buy_from_account_price(client, query):
    await handle_price_change(
        client, query,
        price_key="buy_from_account",
        able_key="buy_from_account",
        stop_text=STOP_BUY,
        stop_keyboard=STOP_BUY_KEYBOARD,
        success_message="✅ قیمت جدید خرید از حساب شما: {price} تومان ثبت شد.",
        stop_message="⛔️ خرید از حساب شما غیرفعال شد.",
        back_func=change_buy_price,
    )

async def change_cash_purchase_price(client, query):
    await handle_price_change(
        client, query,
        price_key="cash_purchase_price",
        able_key="cash_purchase_price",
        stop_text=STOP_BUY,
        stop_keyboard=STOP_BUY_KEYBOARD,
        success_message="✅ قیمت جدید خرید نقدی شما: {price} تومان ثبت شد.",
        stop_message="⛔️ خرید نقدی شما غیرفعال شد.",
        back_func=change_buy_price,
    )

async def change_student_price(client, query):
    await handle_price_change(
        client, query,
        price_key="student_sale_price",
        able_key="student_sale_price",
        stop_text=STOP_SELL,
        stop_keyboard=STOP_SELL_KEYBOARD,
        success_message="✅ قیمت جدید فروش دانشجویی شما: {price} تومان ثبت شد.",
        stop_message="⛔️ فروش دانشجویی شما غیرفعال شد.",
        back_func=sell_price,
    )

async def change_official_sell_price(client, query):
    await handle_price_change(
        client, query,
        price_key="offical_sale_price",
        able_key="offical_sale_price",
        stop_text=STOP_BUY,
        stop_keyboard=STOP_BUY_KEYBOARD,
        success_message="✅ قیمت جدید فروش رسمی شما: {price} تومان ثبت شد.",
        stop_message="⛔️ فروش رسمی شما غیرفعال شد.",
        back_func=sell_price,
    )

async def change_buy_tether_price(client, query):
    await handle_price_change(
        client, query,
        price_key="buy_eth",
        able_key="buy_eth",
        stop_text=STOP_BUY,
        stop_keyboard=STOP_BUY_KEYBOARD,
        success_message="✅ قیمت خرید تتر شما: {price} تومان ثبت شد.",
        stop_message="⛔️ خرید تتر شما غیرفعال شد.",
        back_func=change_buy_price,
    )

async def change_sell_tether_price(client, query):
    await handle_price_change(
        client, query,
        price_key="sell_eth",
        able_key="sell_eth",
        stop_text=STOP_SELL,
        stop_keyboard=STOP_SELL_KEYBOARD,
        success_message="✅ قیمت فروش تتر شما: {price} تومان ثبت شد.",
        stop_message="⛔️ فروش تتر شما غیرفعال شد.",
        back_func=sell_price,
    )

# ============== General Handlers ==============

async def handle_price_change(
    client, query, price_key, able_key, stop_text, stop_keyboard,
    success_message, stop_message, back_func
):
    chat_id = query.message.chat.id
    
    # برای Inline Keyboard، باید از client.ask استفاده کنیم
    new_price_ask = await client.send_message(
        chat_id,
        "✏️ لطفاً قیمت جدید را وارد کنید:",
    )
    
    new_price_message = await client.listen(chat_id=chat_id, user_id=query.from_user.id)
    try:
        text = new_price_message.text.strip()
        value = float(text)
        able[able_key] = True
        formatted_price = toman_form(int(value)) if value.is_integer() else str(value)
        prices[price_key] = formatted_price
        await client.send_message(chat_id, text=success_message.format(price=formatted_price))
    except ValueError:
        await client.send_message(chat_id, text="❗️ لطفاً یک عدد معتبر وارد کنید.")
    except Exception:
        await client.send_message(chat_id, text="⚠️ مشکلی پیش آمد. لطفاً دوباره تلاش کنید.")
    
    await client.delete_messages(chat_id, new_price_ask.id)
    await back_func(client, query)

async def stop_buy(client, query):
    await stop_action(
        client, query,
        stop_keys=["buy_from_account", "cash_purchase_price"],
        success_message="⛔️ تمامی حالت‌های خرید شما با موفقیت متوقف شد.",
    )

async def stop_sell(client, query):
    await stop_action(
        client, query,
        stop_keys=["sell_from_account", "cash_sales_price", "student_sale_price", "offical_sale_price"],
        success_message="⛔️ تمامی حالت‌های فروش شما با موفقیت متوقف شد.",
    )

async def stop_action(client, query, stop_keys, success_message):
    chat_id = query.message.chat.id
    options = ["✅ بله، متوقف کن", "❌ خیر، منصرف شدم"]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=f"confirm_stop_{i}")] for i, opt in enumerate(options)
    ])
    
    await client.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.id,
        text="آیا مطمئن هستید که می‌خواهید همه حالت‌ها را متوقف کنید؟",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^confirm_stop_0$"))
async def confirm_stop_handler(client, callback_query):
    await callback_query.answer()
    chat_id = callback_query.message.chat.id
    
    # متوقف کردن همه کلیدها
    stop_keys = ["buy_from_account", "cash_purchase_price", "sell_from_account", "cash_sales_price", "student_sale_price", "offical_sale_price"]
    for key in stop_keys:
        prices[key] = 0
        able[key] = False
    
    await client.send_message(chat_id, text="⛔️ تمامی حالت‌های خرید و فروش شما با موفقیت متوقف شد.")
    await admin_panel(client, callback_query.message, callback_query.message.chat.id, callback_query.from_user.id)

@Client.on_callback_query(filters.regex(r"^confirm_stop_1$"))
async def decline_stop_handler(client, callback_query):
    await callback_query.answer()
    await client.send_message(callback_query.message.chat.id, text="👌 متوجه شدم. اگر نیاز به راهنمایی دارید، در خدمت شما هستم.")
    await admin_panel(client, callback_query.message, callback_query.message.chat.id, callback_query.from_user.id)
