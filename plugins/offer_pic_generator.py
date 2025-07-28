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
        "farsi_text": 67,
        "farsi_small": 40,
        "eng_text": 55,
        "eng_small": 40,
        "price": 65
    }
    return {
        "farsi_text": ImageFont.truetype("./assets/fonts/Morabba.ttf", font_sizes["farsi_text"]),
        "farsi_small": ImageFont.truetype("./assets/fonts/dirooz.ttf", font_sizes["farsi_small"]),
        "eng_text": ImageFont.truetype("./assets/fonts/montsrrat.otf", font_sizes["eng_text"]),
        "eng_small": ImageFont.truetype("./assets/fonts/montsrrat.otf", font_sizes["eng_small"]),
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

def add_date_to_news():
    now, jalali = get_current_times()
    img = Image.open("./assets/news/news.png").convert("RGBA")
    draw = ImageDraw.Draw(img)
    fonts = load_fonts()

    positions = [(1060, 160), (1050, 35), (105, 180), (55, 65)]
    texts = [
        f"{jalali[0]}/{jalali[1]}/{jalali[2]}",
        get_weekday_fa(now),
        f"{now.year}/{now.day}/{now.month}",
        get_weekday_en(now)
    ]
    font_list = [fonts["farsi_small"], fonts["farsi_text"], fonts["eng_small"], fonts["eng_text"]]
    colors = [(255, 255, 255)] * 4

    draw_text(draw, positions, texts, font_list, colors)
    img.save("./assets/news_date.png")

def offer_draw(state):
    now, _ = get_current_times()
    
    # Check if state is None or invalid
    if state is None or state < 1 or state > 6:
        print("هیچ آفر فعالی موجود نیست یا وضعیت نامعتبر است.")
        return
    
    img_path = f"./assets/offer/offer{state}.png"
    img = Image.open(img_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # فونت‌ها با اندازه‌های مخصوص این بخش
    fonts = {
        "farsi_text": ImageFont.truetype("./assets/fonts/Morabba.ttf", 86),
        "farsi_small": ImageFont.truetype("./assets/fonts/Morabba.ttf", 86),
        "eng_text": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", 83),
        "eng_small": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", 95),
        "price": ImageFont.truetype("./assets/fonts/montsrrat.otf", 220)
    }

    positions = [(1900, 265), (1860, 420), (420, 250), (580, 420)]
    texts = [
        get_farsi_date_str(),
        get_weekday_fa(now),
        get_english_date_str(now),
        get_weekday_en(now)
    ]
    font_list = [fonts["farsi_small"], fonts["farsi_text"], fonts["eng_small"], fonts["eng_text"]]
    colors = [(255, 255, 255)] * 4

    draw_text(draw, positions, texts, font_list, colors)

    # آفرها و فایل خروجی مربوطه
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
                (360, 2030),
                toman_form(price_offers[offer_name]),
                font=fonts["price"],
                fill=(0, 0, 0)
            )
            img.save(f"./assets/{filename}")
            break
    else:
        print("هیچ آفر فعالی موجود نیست.")

def create_image_for_tether_offer():
    now, _ = get_current_times()
    img = Image.open("./assets/offer/tether_buy_sell.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    fonts = {
        "farsi_text": ImageFont.truetype("./assets/fonts/Morabba.ttf", 86),
        "farsi_small": ImageFont.truetype("./assets/fonts/Morabba.ttf", 86),
        "eng_text": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", 83),
        "eng_small": ImageFont.truetype("./assets/fonts/YekanBakh.ttf", 95),
        "price": ImageFont.truetype("./assets/fonts/montsrrat.otf", 230)
    }

    positions = [(1900, 265), (1860, 420), (420, 250), (580, 420)]
    texts = [
        get_farsi_date_str(),
        get_weekday_fa(now),
        get_english_date_str(now),
        get_weekday_en(now)
    ]
    font_list = [fonts["farsi_small"], fonts["farsi_text"], fonts["eng_small"], fonts["eng_text"]]
    colors = [(255, 255, 255)] * 4

    draw_text(draw, positions, texts, font_list, colors)

    price_positions = [
        (1800, 1125),
        (370, 1125),
        (1980, 2070),
        (480, 2070),
    ]

    for i, offer in enumerate(tether_price.keys()):
        if i < len(price_positions):
            draw.text(
                price_positions[i],
                str(tether_price[offer]),
                font=fonts["price"],
                fill=(0, 0, 0)
            )

    save_path = "./assets/eth_offer.png"
    img.save(save_path)
    return save_path

    
    
    for i, offer in enumerate(list(tether_price.keys())):
        draw.text(
            position[i],
            str(tether_price[offer]),
            font=fonts["price"],
            fill=(0, 0, 0)
        )

    save_path = "./assets/eth_offer.png"
    
    img.save(save_path) 
    return save_path
    

# ======================= Auto Run =======================
if __name__ == "__main__":
    create_image_for_tether_offer()

    
