from PIL import Image, ImageFont, ImageDraw
import datetime
import jdatetime

from .data import (
    weekdays,
    call_able,
    prices,
    able,
    current_theme
)

FARSI_MONTHS = [
    "", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]
EN_MONTHS = [
    "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

FONT_PATHS = {
    "yekan": "./assets/fonts/YekanBakh.ttf",
    "montserrat": "./assets/fonts/montsrrat.otf",
    "morabba": "./assets/fonts/Morabba.ttf"
}

FONT_SIZES = {
    "farsi_big": 85,
    "farsi_num": 84,
    "farsi_num_small": 90,
    "eng_big": 120,
    "eng_small": 85,
    "price": 135,
    "rial": 115,
    "call": 100,
}

WEEKDAYS_LOCATION = {
    "Saturday":   [(1920, 410), (610, 420)],
    "Sunday":     [(1870, 410), (650, 420)],
    "Monday":     [(1890, 410), (650, 430)],
    "Tuesday":    [(1870, 405), (640, 415)],
    "Wednesday":  [(1870, 405), (580, 420)],
    "Thursday":   [(1870, 410), (610, 425)],
    "Friday":     [(1965, 420), (680, 425)],
}

PRICE_POSITIONS = [
    ("buy_from_account", (630, 680)),
    ("cash_purchase_price", (630, 1030)),
    ("sell_from_account", (630, 1580)),
    ("cash_sales_price", (630, 1920)),
    ("offical_sale_price", (630, 2260)),
]
STOP_POSITIONS = [
    (550, 680),   # buy_from_account
    (550, 1030),  # cash_purchase_price
    (530, 1580),  # sell_from_account
    (530, 1940),  # cash_sales_price
    (530, 2280),  # offical_sale_price
]
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
    return {
        "farsi_big": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_big"]),
        "farsi_num": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_num"]),
        "farsi_num_small": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_num_small"]),
        "eng_big": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["eng_big"]),
        "eng_small": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["eng_small"]),
        "price": ImageFont.truetype(FONT_PATHS["montserrat"], FONT_SIZES["price"]),
        "rial": ImageFont.truetype(FONT_PATHS["morabba"], FONT_SIZES["rial"]),
        "call": ImageFont.truetype(FONT_PATHS["morabba"], FONT_SIZES["call"]),
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

    # تاریخ و روز فارسی
    farsi_weekday_pos, eng_weekday_pos = WEEKDAYS_LOCATION.get(today_en, ((0,0),(0,0)))
    draw_ctx.text(farsi_weekday_pos, weekdays.get(today_en, ""), font=fonts["farsi_big"], fill="white")
    farsi_date_str = f"{farsi_date['day']}{farsi_date['month']}{farsi_date['year']}"
    draw_ctx.text((1860, 255), farsi_date_str, font=fonts["farsi_num"], fill="white")

    # تاریخ و روز انگلیسی
    eng_date_str = f"{english_date['day']} {english_date['month']} {english_date['year']}"
    draw_ctx.text((390, 230), eng_date_str, font=fonts["eng_big"], fill="white")
    draw_ctx.text(eng_weekday_pos, today_en, font=fonts["eng_small"], fill="white")

    # قیمت‌ها
    for idx, (price_key, price_pos) in enumerate(PRICE_POSITIONS):
        if able.get(price_key):
            draw_ctx.text(price_pos, prices[price_key], font=fonts["price"], fill=(0, 0, 0))
        elif call_able.get(price_key):
            draw_ctx.text(CALL_POSITIONS[idx], "تماس بگیرید", font=fonts["call"], fill=(0, 0, 0))
        else:
            stop_text = "توقف خرید" if idx <= 1 else "توقف فروش"
            draw_ctx.text(STOP_POSITIONS[idx], stop_text, font=fonts["rial"], fill=(0, 0, 0))

    img.save("./assets/prices.png")

if __name__ == "__main__":
    draw()