from PIL import Image, ImageFont, ImageDraw
import datetime
import jdatetime
from .data import *

# ======================= Helper Functions =======================

def get_current_times():
    """دریافت زمان فعلی میلادی و جلالی"""
    now = datetime.datetime.now()
    jalali = jdatetime.date.fromgregorian(day=now.day, month=now.month, year=now.year)
    return now, str(jalali).split("-")

def load_fonts(font_sizes=None):
    """لود فونت‌ها با اندازه‌های دلخواه"""
    font_sizes = font_sizes or {
        "farsi_date": 67,
        "farsi_weekday": 40,
        "english_date": 55,
        "english_weekday": 40,
        "english_number": 55,  # فونت انگلیسی مخصوص عددی
        "price": 65
    }
    return {
        "farsi_date": ImageFont.truetype("./assets/fonts/Morabba.ttf", font_sizes["farsi_date"]),
        "farsi_weekday": ImageFont.truetype("./assets/fonts/dirooz.ttf", font_sizes["farsi_weekday"]),
        "english_date": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", font_sizes["english_date"]),
        "english_weekday": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", font_sizes["english_weekday"]),
        "english_number": ImageFont.truetype("./assets/fonts/montsrrat.otf", font_sizes["english_number"]),  # فونت انگلیسی برای عددی‌ها
        "price": ImageFont.truetype("./assets/fonts/montsrrat.otf", font_sizes["price"])
    }

def draw_text(draw_obj, positions, texts, fonts, colors):
    """رسم چند متن با فونت و رنگ‌های مختلف"""
    for pos, text, font, color in zip(positions, texts, fonts, colors):
        draw_obj.text(pos, text, font=font, fill=color)

def get_farsi_date_str():
    """تاریخ شمسی به صورت رشته"""
    farsi = get_farsi_date()
    return f"{farsi['day']} {farsi['month']} {farsi['year']}"

def get_english_date_str(now):
    """تاریخ میلادی به صورت رشته"""
    eng = get_english_date()
    return f"{eng['year']} {eng['month']} {eng['day']}"

def get_weekday_fa(now):
    """نام روز هفته به فارسی"""
    return weekdays[now.strftime('%A')]

def get_weekday_en(now):
    """نام روز هفته به انگلیسی"""
    return now.strftime('%A')

# ======================= Main Functions =======================

# پوزیشن‌های دقیق هر متن روی بنر آفر
OFFER_TEXT_POSITIONS = {
    "farsi_date": (1900, 250),         # تاریخ شمسی
    "farsi_weekday": (1860, 420),      # روز هفته شمسی
    "english_date": (420, 250),        # تاریخ میلادی
    "english_weekday": (580, 420),     # روز هفته میلادی
    "price": (360, 2100),              # قیمت آفر
    "tether_buy_irr": (1800, 1125),    # قیمت خرید تتر (ریال)
    "tether_sell_irr": (370, 1125),    # قیمت فروش تتر (ریال)
    "tether_buy_gbp": (1980, 2070),    # قیمت خرید تتر (پوند)
    "tether_sell_gbp": (480, 2070),    # قیمت فروش تتر (پوند)
}

OFFER_FONT_SIZES = {
    "farsi_date": 115,
    "farsi_weekday": 86,
    "english_date": 100,
    "english_weekday": 95,
    "english_number": 115,
    "price": 220,
    "tether_price": 230
}

def load_offer_fonts():
    return {
        "farsi_date": ImageFont.truetype("./assets/fonts/Morabba.ttf", OFFER_FONT_SIZES["farsi_date"]),
        "farsi_weekday": ImageFont.truetype("./assets/fonts/Morabba.ttf", OFFER_FONT_SIZES["farsi_weekday"]),
        "english_date": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", OFFER_FONT_SIZES["english_date"]),
        "english_weekday": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", OFFER_FONT_SIZES["english_weekday"]),
        "english_number": ImageFont.truetype("./assets/fonts/montsrrat.otf", OFFER_FONT_SIZES["english_number"]),
        "price": ImageFont.truetype("./assets/fonts/montsrrat.otf", OFFER_FONT_SIZES["price"]),
        "tether_price": ImageFont.truetype("./assets/fonts/montsrrat.otf", OFFER_FONT_SIZES["tether_price"])
    }

def add_date_to_news():
    now, jalali = get_current_times()
    img = Image.open("./assets/news/news.png").convert("RGBA")
    draw = ImageDraw.Draw(img)
    fonts = load_fonts()

    # پوزیشن‌ها و فونت‌ها و متن‌ها به صورت واضح
    positions = [
        (1060, 160),  # تاریخ شمسی
        (1050, 35),   # روز هفته شمسی
        (105, 180),   # تاریخ میلادی
        (55, 65)      # روز هفته میلادی
    ]
    texts = [
        f"{jalali[0]}/{jalali[1]}/{jalali[2]}",  # تاریخ شمسی
        get_weekday_fa(now),                     # روز هفته شمسی
        f"{now.year}/{now.day}/{now.month}",     # تاریخ میلادی
        get_weekday_en(now)                      # روز هفته میلادی
    ]
    font_list = [
        fonts["farsi_date"],
        fonts["farsi_weekday"],
        fonts["english_number"],
        fonts["english_date"]
    ]
    colors = [(255, 255, 255)] * 4

    draw_text(draw, positions, texts, font_list, colors)
    img.save("./assets/news_date.png")

def offer_draw(state):
    now, _ = get_current_times()
    # Check if state is None or invalid
    if state is None or state < 1 or state > 6:
        # فقط در حالت تست پرینت کن
        if __name__ == "__main__":
            print("هیچ آفر فعالی موجود نیست یا وضعیت نامعتبر است.")
        return

    img_path = f"./assets/offer/offer{state}.png"
    img = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    fonts = load_offer_fonts()
    # پوزیشن‌ها و متن‌ها و فونت‌ها به صورت واضح
    positions = [
        OFFER_TEXT_POSITIONS["farsi_date"],
        OFFER_TEXT_POSITIONS["farsi_weekday"],
        OFFER_TEXT_POSITIONS["english_date"],
        OFFER_TEXT_POSITIONS["english_weekday"]
    ]
    texts = [
        get_farsi_date_str(),         # تاریخ شمسی
        get_weekday_fa(now),          # روز هفته شمسی
        get_english_date_str(now),    # تاریخ میلادی
        get_weekday_en(now)           # روز هفته میلادی
    ]
    font_list = [
        fonts["farsi_date"],
        fonts["farsi_weekday"],
        fonts["english_number"],
        fonts["english_date"]
    ]
    colors = [(255, 255, 255)] * 4

    draw_text(draw, positions, texts, font_list, colors)

    offers = [
        ("خرید ویژه نقدی", "offer1.png"),
        ("خرید ویژه از حساب", "offer2.png"),
        ("خرید ویژه تتر", "offer3.png"),
        ("فروش ویژه نقدی", "offer4.png"),
        ("فروش ویژه از حساب", "offer5.png"),
        ("فروش ویژه تتر", "offer6.png"),
    ]

    for offer_name, filename in offers:
        if able_offers.get(offer_name):
            draw.text(
                OFFER_TEXT_POSITIONS["price"],
                toman_form(price_offers[offer_name]),
                font=fonts["price"],
                fill=(0, 0, 0)
            )
            img.save(f"./assets/{filename}")
            break
    else:
        # فقط در حالت تست پرینت کن
        if __name__ == "__main__":
            print("هیچ آفر فعالی موجود نیست.")

def create_image_for_tether_offer():
    now, _ = get_current_times()
    img = Image.open("./assets/offer/tether_buy_sell.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    fonts = load_offer_fonts()
    positions = [
        OFFER_TEXT_POSITIONS["farsi_date"],
        OFFER_TEXT_POSITIONS["farsi_weekday"],
        OFFER_TEXT_POSITIONS["english_date"],
        OFFER_TEXT_POSITIONS["english_weekday"]
    ]
    texts = [
        get_farsi_date_str(),
        get_weekday_fa(now),
        get_english_date_str(now),
        get_weekday_en(now)
    ]
    font_list = [
        fonts["farsi_date"],
        fonts["farsi_weekday"],
        fonts["english_number"],
        fonts["english_date"]
    ]
    colors = [(255, 255, 255)] * 4

    draw_text(draw, positions, texts, font_list, colors)

    # پوزیشن‌های قیمت تتر به صورت واضح
    tether_price_positions = [
        OFFER_TEXT_POSITIONS["tether_buy_irr"],
        OFFER_TEXT_POSITIONS["tether_sell_irr"],
        OFFER_TEXT_POSITIONS["tether_buy_gbp"],
        OFFER_TEXT_POSITIONS["tether_sell_gbp"]
    ]

    for i, offer in enumerate(tether_price.keys()):
        if i < len(tether_price_positions):
            draw.text(
                tether_price_positions[i],
                str(tether_price[offer]),
                font=fonts["tether_price"],
                fill=(0, 0, 0)
            )

    save_path = "./assets/eth_offer.png"
    img.save(save_path)
    return save_path

# ======================= Test Mode =======================
if __name__ == "__main__":
    # حالت تستی: تمام آفرها فعال و قیمت تستی
    import copy

    TEST_PRICE = 128000

    offers = [
        ("خرید ویژه نقدی", "offer1.png"),
        ("خرید ویژه از حساب", "offer2.png"),
        ("خرید ویژه تتر", "offer3.png"),
        ("فروش ویژه نقدی", "offer4.png"),
        ("فروش ویژه از حساب", "offer5.png"),
        ("فروش ویژه تتر", "offer6.png"),
    ]

    tether_offer_keys = list(tether_price.keys())
    test_tether_prices = {k: TEST_PRICE for k in tether_offer_keys}

    now, jalali = get_current_times()

    fonts = load_offer_fonts()
    # پوزیشن‌ها و فونت‌ها به صورت واضح
    positions = [
        OFFER_TEXT_POSITIONS["farsi_date"],
        OFFER_TEXT_POSITIONS["farsi_weekday"],
        OFFER_TEXT_POSITIONS["english_date"],
        OFFER_TEXT_POSITIONS["english_weekday"]
    ]
    price_position = OFFER_TEXT_POSITIONS["price"]
    tether_price_positions = [
        OFFER_TEXT_POSITIONS["tether_buy_irr"],
        OFFER_TEXT_POSITIONS["tether_sell_irr"],
        OFFER_TEXT_POSITIONS["tether_buy_gbp"],
        OFFER_TEXT_POSITIONS["tether_sell_gbp"]
    ]

    for idx, (offer_name, filename) in enumerate(offers, 1):
        try:
            img_path = f"./assets/offer/offer{idx}.png"
            img = Image.open(img_path).convert("RGBA")
            draw = ImageDraw.Draw(img)

            texts = [
                f"{jalali[0]}/{jalali[1]}/{jalali[2]}",  # تاریخ شمسی
                get_weekday_fa(now),                     # روز هفته شمسی
                f"{now.year}/{now.day}/{now.month}",     # تاریخ میلادی
                get_weekday_en(now)                      # روز هفته میلادی
            ]
            font_list = [
                fonts["farsi_date"],
                fonts["farsi_weekday"],
                fonts["english_number"],
                fonts["english_date"]
            ]
            colors = [(255, 255, 255)] * 4

            draw_text(draw, positions, texts, font_list, colors)

            draw.text(
                price_position,
                toman_form(TEST_PRICE),
                font=fonts["price"],
                fill=(0, 0, 0)
            )
            img.save(f"./assets/{filename}")
            print(f"✅ Test banner {filename} created.")
        except Exception as e:
            print(f"❌ Error creating test banner {filename}: {e}")
            import traceback
            print(traceback.format_exc())

    # تولید بنر تتر تستی
    try:
        img = Image.open("./assets/offer/tether_buy_sell.png").convert("RGBA")
        draw = ImageDraw.Draw(img)

        texts = [
            f"{jalali[0]}/{jalali[1]}/{jalali[2]}",  # تاریخ شمسی
            get_weekday_fa(now),                     # روز هفته شمسی
            f"{now.year}/{now.day}/{now.month}",     # تاریخ میلادی
            get_weekday_en(now)                      # روز هفته میلادی
        ]
        font_list = [
            fonts["farsi_date"],
            fonts["farsi_weekday"],
            fonts["english_number"],
            fonts["english_date"]
        ]
        colors = [(255, 255, 255)] * 4

        draw_text(draw, positions, texts, font_list, colors)

        for i, offer in enumerate(tether_offer_keys):
            if i < len(tether_price_positions):
                draw.text(
                    tether_price_positions[i],
                    str(TEST_PRICE),
                    font=fonts["tether_price"],
                    fill=(0, 0, 0)
                )

        save_path = "./assets/eth_offer.png"
        img.save(save_path)
        print(f"✅ Test Tether banner created: {save_path}")
    except Exception as e:
        print(f"❌ Error creating test Tether banner: {e}")
