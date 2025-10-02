
# ===================== Imports =====================
import datetime
from datetime import timezone
from hashlib import md5
import json
import requests
import random
import jdatetime
from pyrogram import emoji
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json

URL = "https://sarafipardis.co.uk/wp-json/pardis/v1/rates"
API_KEY = "PX9k7mN2qR8vL4jH6wE3tY1uI5oP0aS9dF7gK2mN8xZ4cV6bQ1wE3rT5yU8iO0pL"




# ===================== Constants =====================

CHANNEL_ID = "@sarafipardis"
# CHANNEL_ID = "@pardis_addon"

ADMINS = [558994996, 474945045, 672452907, 1664374014]

let_keyboard = True

COMMANDS = [
    f"تغییر قیمت {emoji.BAR_CHART}",
    f"خرید/فروش ویژه {emoji.LOUDSPEAKER}",
    "نشر اعلانات",
    "تغییر قیمت تتر",
    f"نهایی کردن قیمت ها {emoji.WRITING_HAND_LIGHT_SKIN_TONE}",
    f"استعلام قیمت {emoji.POUND_BANKNOTE}",
    "تبدیل ارز",
]

# ===================== Static Data =====================

prices = {
    "buy_from_account": "0",
    "cash_purchase_price": "0",
    "sell_from_account": "0",
    "cash_sales_price": "0",
    "offical_sale_price": "0",
}

able = {k: False for k in prices}
call_able = {k: False for k in prices}

offer_labels = [
    "خرید ویژه نقدی",
    "خرید ویژه از حساب",
    "خرید ویژه تتر",
    "فروش ویژه نقدی", 
    "فروش ویژه از حساب",
    "فروش ویژه تتر",
]

able_offers = {k: False for k in offer_labels}
price_offers = {k: 0 for k in offer_labels}

weekdays = {
    "Saturday": "شنبه",
    "Sunday": "یک شنبه",
    "Monday": "دوشنبه",
    "Tuesday": "سه شنبه",
    "Wednesday": "چهارشنبه",
    "Thursday": "پنج شنبه",
    "Friday": "جمعه",
}

pound_price = {
    "pound_buy_irr": 0,
    "pound_sell_irr": 0,
    "pound_buy_gbp": 0,
    "pound_sell_gbp": 0,
}

tether_price = {
    "tether_buy_irr": 0,
    "tether_sell_irr": 0,
    "tether_buy_gbp": 0,
    "tether_sell_gbp": 0,
}

# ===================== Global Variables =====================
admin_id = []

# ===================== Functions =====================



def send_request(currency, rate):
    payload = {"currency": currency, "rate": rate, "api_key": API_KEY}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending {currency}:", e)
    except json.JSONDecodeError:
        print(f"❌ JSON decode error for {currency}")

# توابع مخصوص هر ارز
def send_gbp_buy(rate): return send_request("GBP_BUY", rate)
def send_gbp_sell(rate): return send_request("GBP_SELL", rate)
def send_usdt_buy(rate): return send_request("USDT_BUY", rate)
def send_usdt_sell(rate): return send_request("USDT_SELL", rate)



def get_farsi_date():
    today = jdatetime.date.today()
    months = [
        "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    return {
        "day": str(today.day),
        "month": months[today.month],
        "year": today.year
    }

def get_english_date():
    today = datetime.date.today()
    months = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    return {
        "day": today.day,
        "month": months[today.month],
        "year": today.year
    }

async def insert_admin_stuff_to_data(user_id, chat_id):
    """اضافه کردن آی‌دی ادمین به لیست"""
    admin_id.clear()
    admin_id.extend([user_id, chat_id])

def current_theme():
    return random.randint(1, 8)

def get_url() -> str:
    """ساختن URL برای ارسال اطلاعات قیمت"""
    secret_key = "n54fD5bLgcYsaPKSfBD6JeGCzaA4Z6PmXxhicEcEejzC3fumsY"
    gmt_date = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d")
    full_key = f"{secret_key}_{gmt_date}"
    hashed_key = md5(full_key.encode()).hexdigest()
    return (
        "https://sarafipardis.co.uk/wp-admin/admin-ajax.php"
        f"?action=ejkvs_savedata&key={hashed_key}"
    )

def send_data() -> int:
    """ارسال قیمت‌ها به سرور"""
    headers = {"Content-Type": "application/json"}
    response = requests.post(get_url(), data=json.dumps(prices), headers=headers)
    return response.status_code

async def change_price(client, message):
    """نمایش دکمه‌های تغییر قیمت خرید یا فروش"""
    from .message_manager import get_back_button
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("قیمت خرید", callback_data="buy"),
            InlineKeyboardButton("قیمت فروش", callback_data="sell"),
        ],
        [get_back_button("back_to_admin", "🔙 بازگشت به پنل ادمین")]
    ])
    await message.reply(
        "قیمت کدام بخش را میخواهید تغییر دهید؟",
        quote=True,
        reply_markup=keyboard,
    )

def get_state() -> int | None:
    """برگرداندن وضعیت فعال پیشنهادات ویژه"""
    for idx, label in enumerate(offer_labels, 1):
        if able_offers[label]:
            return idx
    return None

def turn_all_offers_false():
    """خاموش کردن همه‌ی پیشنهادات ویژه"""
    for offer in able_offers:
        able_offers[offer] = False

def turn_all_calls_false():
    """خاموش کردن همه‌ی تماس ها"""
    for offer in call_able:
        call_able[offer] = False

def add_price_to_call(price):
    call_able[price] = True

def toman_form(price):
    s = str(price)
    if not s.isdigit():
        return s
    return "{:,}".format(int(s))

def get_price(price_type):
    """دریافت قیمت بر اساس نوع"""
    return float(prices.get(price_type, 0))

def get_tether_price(is_buy=True):
    """دریافت قیمت تتر بر اساس خرید یا فروش"""
    if is_buy:
        return float(tether_price.get("tether_buy_irr", 0))
    else:
        return float(tether_price.get("tether_sell_irr", 0))

def safe_int(value):
    """
    تبدیل ایمن رشته یا عدد به int
    - حذف کاما
    - اگر None یا '' باشد، برمی‌گرداند 0
    """
    if not value:
        return 0
    if isinstance(value, int):
        return value
    # حذف کاما و فاصله
    value = str(value).replace(",", "").strip()
    try:
        return int(value)
    except ValueError:
        return 0

##############################################################################
