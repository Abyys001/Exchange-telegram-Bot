from PIL import Image, ImageFont, ImageDraw
import datetime
import jdatetime

# from .data import (
#     weekdays,
#     call_able,
#     prices,
#     able,
#     current_theme
# )

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



FARSI_MONTHS = [
    "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]
EN_MONTHS = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# -------------------------------
# فونت‌ها و سایزها و کاربرد هرکدام:
# -------------------------------
# "yekan"      : فونت فارسی (برای روز هفته فارسی، تاریخ فارسی)
# "montserrat" : فونت انگلیسی (برای قیمت‌ها)
# "morabba"    : فونت ضخیم (برای توقف/ریال و تماس بگیرید)
#
# سایزها:
#   - farsi_big:      85   (روز هفته فارسی)
#   - farsi_num:      84   (تاریخ فارسی)
#   - farsi_num_small:90   (استفاده نشده فعلا)
#   - eng_big:        120  (تاریخ انگلیسی)
#   - eng_small:      85   (روز هفته انگلیسی)
#   - price:          135  (قیمت‌ها)
#   - rial:           115  (توقف خرید/فروش)
#   - call:           100  (تماس بگیرید)
# -------------------------------

FONT_PATHS = {
    "yekan": "./assets/fonts/YekanBakh.ttf",        # فارسی
    "montserrat": "./assets/fonts/montsrrat.otf",   # انگلیسی
    "morabba": "./assets/fonts/Morabba.ttf"         # ضخیم
}

FONT_SIZES = {
    # فارسی
    "farsi_big": 89,         # روز هفته فارسی (مثلا: "دوشنبه")
    "farsi_num": 100,         # تاریخ فارسی (مثلا: "۲۳ خرداد ۱۴۰۳")
    "farsi_num_small": 90,   # (فعلا استفاده نشده)
    # انگلیسی
    "eng_big": 120,          # تاریخ انگلیسی (مثلا: "12 Jun 2024")
    "eng_small": 85,         # روز هفته انگلیسی (مثلا: "Monday")
    # قیمت و وضعیت
    "price": 135,            # قیمت‌ها (مثلا: "۶۵,۰۰۰")
    "rial": 115,             # توقف خرید/فروش ("توقف خرید" یا "توقف فروش")
    "call": 100,             # تماس بگیرید ("تماس بگیرید")
}

# موقعیت‌های نمایش روز هفته (فارسی و انگلیسی)
# [0]: موقعیت روز هفته فارسی (فونت: yekan, سایز: farsi_big)
# [1]: موقعیت روز هفته انگلیسی (فونت: yekan, سایز: eng_small)
WEEKDAYS_LOCATION = {
    "Saturday":   [(1920, 410), (610, 420)],
    "Sunday":     [(1870, 410), (650, 420)],
    "Monday":     [(1890, 410), (650, 430)],
    "Tuesday":    [(1870, 405), (640, 415)],
    "Wednesday":  [(1870, 405), (580, 420)],
    "Thursday":   [(1870, 410), (610, 425)],
    "Friday":     [(1965, 420), (680, 425)],
}

# موقعیت قیمت‌ها
# هر سطر: (کلید قیمت, موقعیت)
# فونت: montserrat, سایز: price
PRICE_POSITIONS = [
    ("buy_from_account", (630, 680)),
    ("cash_purchase_price", (630, 1030)),
    ("sell_from_account", (630, 1580)),
    ("cash_sales_price", (630, 1920)),
    ("offical_sale_price", (630, 2260)),
]

# موقعیت متن توقف خرید/فروش
# فونت: morabba, سایز: rial
STOP_POSITIONS = [
    (550, 680),   # buy_from_account
    (550, 1030),  # cash_purchase_price
    (530, 1580),  # sell_from_account
    (530, 1940),  # cash_sales_price
    (530, 2280),  # offical_sale_price
]

# موقعیت متن "تماس بگیرید"
# فونت: morabba, سایز: call
CALL_POSITIONS = [
    (530, 690),   # buy_from_account
    (530, 1030),  # cash_purchase_price
    (530, 1580),  # sell_from_account
    (530, 1940),  # cash_sales_price
    (530, 2280),  # offical_sale_price
]

def get_farsi_date():
    today = jdatetime.date.today()
    return {
        "day": str(today.day),
        "month": FARSI_MONTHS[today.month],
        "year": today.year
    }

def get_english_date():
    today = datetime.date.today()
    return {
        "day": today.day,
        "month": EN_MONTHS[today.month],
        "year": today.year
    }

def load_fonts():
    """
    فونت‌های مورد استفاده و کاربرد هرکدام:
      - farsi_big:      روز هفته فارسی (فونت: yekan, سایز: 85)
      - farsi_num:      تاریخ فارسی (فونت: yekan, سایز: 84)
      - eng_big:        تاریخ انگلیسی (فونت: yekan, سایز: 120)
      - eng_small:      روز هفته انگلیسی (فونت: yekan, سایز: 85)
      - price:          قیمت‌ها (فونت: montserrat, سایز: 135)
      - rial:           توقف خرید/فروش (فونت: morabba, سایز: 115)
      - call:           تماس بگیرید (فونت: morabba, سایز: 100)
    """
    return {
        "farsi_big": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_big"]),         # روز هفته فارسی
        "farsi_num": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_num"]),         # تاریخ فارسی
        "farsi_num_small": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_num_small"]), # (فعلا استفاده نشده)
        "eng_big": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["eng_big"]),             # تاریخ انگلیسی
        "eng_small": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["eng_small"]),         # روز هفته انگلیسی
        "price": ImageFont.truetype(FONT_PATHS["montserrat"], FONT_SIZES["price"]),            # قیمت‌ها
        "rial": ImageFont.truetype(FONT_PATHS["morabba"], FONT_SIZES["rial"]),                 # توقف خرید/فروش
        "call": ImageFont.truetype(FONT_PATHS["morabba"], FONT_SIZES["call"]),                 # تماس بگیرید
    }

def draw():
    now = datetime.datetime.now()
    today_en = now.strftime('%A')
    farsi_date = get_farsi_date()
    english_date = get_english_date()

    # باز کردن عکس پس زمینه
    img_path = f"./assets/price_theme/{current_theme()}.png"
    img = Image.open(img_path).convert("RGBA")
    draw_ctx = ImageDraw.Draw(img)

    fonts = load_fonts()

    # --- تاریخ و روز هفته فارسی ---
    # روز هفته فارسی: فونت yekan، سایز farsi_big
    farsi_weekday_pos, eng_weekday_pos = WEEKDAYS_LOCATION.get(today_en, ((0,0),(0,0)))
    draw_ctx.text(farsi_weekday_pos, weekdays.get(today_en, ""), font=fonts["farsi_big"], fill="white")

    # تاریخ فارسی: فونت yekan، سایز farsi_num
    farsi_date_str = f"{farsi_date['day']}{farsi_date['month']}{farsi_date['year']}"
    draw_ctx.text((1900, 255), farsi_date_str, font=fonts["farsi_num"], fill="white")

    # --- تاریخ و روز هفته انگلیسی ---
    # تاریخ انگلیسی: فونت yekan، سایز eng_big
    eng_date_str = f"{english_date['day']} {english_date['month']} {english_date['year']}"
    draw_ctx.text((390, 230), eng_date_str, font=fonts["eng_big"], fill="white")

    # روز هفته انگلیسی: فونت yekan، سایز eng_small
    draw_ctx.text(eng_weekday_pos, today_en, font=fonts["eng_small"], fill="white")

    # --- قیمت‌ها و وضعیت ---
    for idx, (price_key, price_pos) in enumerate(PRICE_POSITIONS):
        if able.get(price_key):
            # قیمت: فونت montserrat، سایز price
            draw_ctx.text(price_pos, prices[price_key], font=fonts["price"], fill=(0, 0, 0))
        elif call_able.get(price_key):
            # تماس بگیرید: فونت morabba، سایز call
            draw_ctx.text(CALL_POSITIONS[idx], "تماس بگیرید", font=fonts["call"], fill=(0, 0, 0))
        else:
            # توقف خرید/فروش: فونت morabba، سایز rial
            stop_text = "توقف خرید" if idx <= 1 else "توقف فروش"
            draw_ctx.text(STOP_POSITIONS[idx], stop_text, font=fonts["rial"], fill=(0, 0, 0))

    img.save("./assets/prices.png")

if __name__ == "__main__":
    draw()  