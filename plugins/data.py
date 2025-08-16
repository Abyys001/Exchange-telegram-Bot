
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

tether_price = {
    "tether_buy_irr": 0,
    "tether_sell_irr": 0,
    "tether_buy_gbp": 0,
    "tether_sell_gbp": 0,
}

# ===================== Global Variables =====================
admin_id = []

# ===================== Functions =====================

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
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("قیمت خرید", "buy"),
            InlineKeyboardButton("قیمت فروش", "sell"),
        ]
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

##############################################################################
