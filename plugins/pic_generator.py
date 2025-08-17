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
    "eng_big_smaller": 100,  # تاریخ انگلیسی با 2 درجه کوچکتر
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

def to_english_digits(s):
    # تبدیل اعداد فارسی یا عربی به انگلیسی
    # اگر ورودی int بود، به str تبدیل می‌کند
    if isinstance(s, int):
        s = str(s)
    farsi_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    table = str.maketrans(
        ''.join(farsi_digits) + ''.join(arabic_digits),
        ''.join(english_digits) * 2
    )
    return str(s).translate(table)

def load_fonts():
    """
    فونت‌های مورد استفاده و کاربرد هرکدام:
      - farsi_big:      روز هفته فارسی (فونت: yekan, سایز: 85)
      - farsi_num:      تاریخ فارسی (فونت: yekan, سایز: 84)
      - eng_big:        تاریخ انگلیسی (فونت: yekan, سایز: 120)
      - eng_big_smaller:تاریخ انگلیسی (فونت: yekan, سایز: 100)
      - eng_small:      روز هفته انگلیسی (فونت: yekan, سایز: 85)
      - price:          قیمت‌ها (فونت: montserrat, سایز: 135)
      - rial:           توقف خرید/فروش (فونت: morabba, سایز: 115)
      - call:           تماس بگیرید (فونت: morabba, سایز: 100)
    """
    return {
        "farsi_big": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_big"]),         # روز هفته فارسی
        "farsi_num": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_num"]),         # تاریخ فارسی
        "farsi_num_small": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["farsi_num_small"]), # (فعلا استفاده نشده)
        "eng_big": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["eng_big"]),             # تاریخ انگلیسی (قبلی)
        "eng_big_smaller": ImageFont.truetype(FONT_PATHS["yekan"], FONT_SIZES["eng_big_smaller"]), # تاریخ انگلیسی با سایز کوچکتر
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
    # تاریخ انگلیسی: اعداد انگلیسی و فونت 2 درجه کوچکتر
    eng_day = to_english_digits(english_date['day'])
    eng_year = to_english_digits(english_date['year'])
    eng_date_str = f"{eng_day} {english_date['month']} {eng_year}"
    draw_ctx.text((390, 230), eng_date_str, font=fonts["eng_big_smaller"], fill="white")

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