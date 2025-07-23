from pyromod import Client
from pyrogram import filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup

from .data import prices, able, toman_form, add_price_to_call
from .admin_panel import admin_panel  # type: ignore

# ============== Constants ==============
STOP_BUY = "⛔️ توقف این حالت از خرید"
STOP_SELL = "⛔️ توقف این حالت از فروش"
MAKE_CALL = "📞 تماس بگیرید"

BUY_FORMS = [
    "💳 تغییر قیمت خرید از حساب",
    "💵 تغییر قیمت خرید نقدی",
    "⛔️ توقف همه خریدها",
    "🔙 بازگشت به منوی اصلی",
]

SELL_FORMS = [
    "💳 تغییر قیمت فروش از حساب",
    "💵 تغییر قیمت فروش نقدی",
    "🏦 تغییر قیمت رسمی",
    "⛔️ توقف همه فروش‌ها",
    "🔙 بازگشت به منوی اصلی",
]

def get_stop_keyboard(stop_text):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(MAKE_CALL)],
            [KeyboardButton(stop_text)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

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
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BUY_FORMS[0]), KeyboardButton(BUY_FORMS[1])],
            [KeyboardButton(BUY_FORMS[2])],
            [KeyboardButton(BUY_FORMS[3])]
        ],
        resize_keyboard=True,
    )

def get_sell_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(SELL_FORMS[0]), KeyboardButton(SELL_FORMS[1])],
            [KeyboardButton(SELL_FORMS[2]), KeyboardButton(SELL_FORMS[3])],
            [KeyboardButton(SELL_FORMS[4])],
        ],
        resize_keyboard=True,
    )

@Client.on_callback_query(filters.regex(r"^buy$"))
async def change_buy_price(client, callback_query):
    chat_id = callback_query.message.chat.id
    buy_form = await client.ask(
        chat_id=chat_id,
        text="🛒 لطفاً نوع خریدی که می‌خواهید تغییر دهید را انتخاب کنید:",
        filters=filters.text,
        reply_markup=get_buy_keyboard(),
    )
    action_map = get_buy_action_map()
    action = action_map.get(buy_form.text)
    if action:
        await action(client, callback_query)

@Client.on_callback_query(filters.regex(r"^sell$"))
async def sell_price(client, callback_query):
    chat_id = callback_query.message.chat.id
    sell_form = await client.ask(
        chat_id=chat_id,
        text="💰 لطفاً نوع فروشی که می‌خواهید تغییر دهید را انتخاب کنید:",
        filters=filters.text,
        reply_markup=get_sell_keyboard(),
    )
    action_map = get_sell_action_map()
    action = action_map.get(sell_form.text)
    if action:
        await action(client, callback_query)

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
    new_price_ask = await client.send_message(
        chat_id,
        "✏️ لطفاً قیمت جدید را وارد کنید یا یکی از گزینه‌های زیر را انتخاب نمایید:",
        reply_markup=stop_keyboard,
    )
    new_price_message = await client.listen(chat_id=chat_id, user_id=query.from_user.id)
    try:
        text = new_price_message.text.strip()
        if text == stop_text:
            prices[price_key] = 0
            able[able_key] = False
            await client.send_message(chat_id, text=stop_message)
        elif text == MAKE_CALL:
            add_price_to_call(able_key)
            await client.send_message(chat_id, "📞 درخواست تماس شما با موفقیت ثبت شد. لطفاً منتظر تماس باشید.")
        else:
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
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(opt)] for opt in options],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    answer = await client.ask(
        chat_id,
        text="آیا مطمئن هستید که می‌خواهید همه حالت‌ها را متوقف کنید؟",
        reply_markup=keyboard,
    )
    if answer.text == options[0]:
        for key in stop_keys:
            prices[key] = 0
            able[key] = False
        await client.send_message(chat_id, text=success_message)
    else:
        await client.send_message(chat_id, text="👌 متوجه شدم. اگر نیاز به راهنمایی دارید، در خدمت شما هستم.")
    await client.delete_messages(chat_id, answer.id)
    await admin_panel(client, query.message, query.message.chat.id, query.from_user.id)
