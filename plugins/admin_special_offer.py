from pathlib import Path
from os import getcwd
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyrogram import emoji
import traceback
import logging

from .data import (
    admin_id, turn_all_offers_false, toman_form,
    able_offers, price_offers, get_state, CHANNEL_ID
)
from .offer_pic_generator import offer_draw

import sys
import types

# Patch the offer_pic_generator module if needed
if ".offer_pic_generator" in sys.modules:
    offer_pic_gen_mod = sys.modules[".offer_pic_generator"]
elif "plugins.offer_pic_generator" in sys.modules:
    offer_pic_gen_mod = sys.modules["plugins.offer_pic_generator"]
else:
    offer_pic_gen_mod = None

if offer_pic_gen_mod and not hasattr(offer_pic_gen_mod, "datetime"):
    import datetime as _real_datetime
    offer_pic_gen_mod.datetime = _real_datetime

# ============== SPECIAL OFFER HANDLER ==============

OFFER_LABELS = [
    "💳 خرید ویژه از حساب",
    "💵 خرید ویژه نقدی",
    "💲 خرید ویژه تتر",
    "💳 فروش ویژه از حساب",
    "💵 فروش ویژه نقدی",
    "�� فروش ویژه تتر",
]
# نگاشت لیبل‌های با ایموجی به لیبل‌های اصلی بدون ایموجی (مطابق data.py)
OFFER_LABELS_MAP = {
    "💵 خرید ویژه نقدی": "خرید ویژه نقدی",
    "💳 خرید ویژه از حساب": "خرید ویژه از حساب",
    "💲 خرید ویژه تتر": "خرید ویژه تتر",
    "💵 فروش ویژه نقدی": "فروش ویژه نقدی",
    "💳 فروش ویژه از حساب": "فروش ویژه از حساب",
    "💲 فروش ویژه تتر": "فروش ویژه تتر",
}
FINALIZE_LABEL = "✅ نهایی‌سازی خرید/فروش ویژه"
BACK_LABEL = "🔙 بازگشت به منوی اصلی"
CANCEL_LABEL = "❌ انصراف"
CONFIRM_LABEL = "✅ بله، نهایی کن"
DECLINE_LABEL = "🔄 خیر، نیاز به تغییر دارم"

MAIN_TEXT = (
    "💷 خرید فروش تتر و پوند نقدی و حسابی\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "Mr. Mahdi    📞  +447533544249\n\n"
    "Ms. Kianian    📞  +989121894230\n\n"
    "Manager  📞  +447399990340\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n"
    "📌آدرس دفتر :\n"
    "<u>Office A\n"
    "708A High Road\n"
    "North Finchley\n"
    "N129QL<u/>\n\n"
    "🔺🔺🔺🔺🔺🔺🔺🔺🔺\n\n"
    "مبالغ زیر ۱۰۰۰ پوند شامل ۱۰ پوند کارمزد می‌باشد\n\n"
    "⛔ لطفا بدون هماهنگی هیچ مبلغی به هیچ حسابی واریز نکنید ⛔"
)

def get_offer_keyboard():
    return ReplyKeyboardMarkup(
        [
            [OFFER_LABELS[0], OFFER_LABELS[1]],
            [OFFER_LABELS[2], OFFER_LABELS[3]],
            [OFFER_LABELS[4]],
            [OFFER_LABELS[5]],
            [FINALIZE_LABEL],
            [BACK_LABEL],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(CANCEL_LABEL)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_confirm_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(CONFIRM_LABEL), KeyboardButton(DECLINE_LABEL)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

async def special_offer(client, message, user_id=None, chat_id=None):
    """
    منوی خرید/فروش ویژه ادمین
    """
    try:
        keyboard = get_offer_keyboard()
        await client.send_message(
            message.chat.id,
            text="لطفاً نوع خرید یا فروش ویژه مورد نظر خود را انتخاب کنید:",
            reply_markup=keyboard
        )
        answer = await client.listen(message.chat.id)
        text = answer.text.strip() if answer.text else ""

        if text in OFFER_LABELS:
            await offer_handler(client, message, offer=text, user_id=user_id, chat_id=chat_id)
        elif text == FINALIZE_LABEL:
            await offer_finalize(client, message, user_id, chat_id)
        elif text == BACK_LABEL:
            await message.reply("✅ به منوی اصلی بازگشتید.")
        else:
            await message.reply("⚠️ لطفاً فقط از میان گزینه‌های موجود انتخاب کنید.")
            await special_offer(client, message, user_id, chat_id)
    except Exception as e:
        logging.error(f"[special_offer] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی رخ داد. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
            f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        )

async def offer_handler(client, message, offer, user_id=None, chat_id=None):
    """
    ثبت قیمت برای یک پیشنهاد ویژه
    """
    try:
        await client.send_message(
            message.chat.id,
            text=f"💰 لطفاً قیمت {offer} را وارد کنید:",
            reply_markup=get_cancel_keyboard()
        )
        offer_price = await client.listen(message.chat.id)
        if not offer_price or not hasattr(offer_price, "text"):
            await message.reply("❗️ ورودی نامعتبر است. لطفاً مجدداً تلاش کنید.")
            return await offer_handler(client, message, offer, user_id=user_id, chat_id=chat_id)

        if offer_price.text == CANCEL_LABEL:
            turn_all_offers_false()
            await message.reply("⏪ عملیات لغو شد و به منوی اصلی بازگشتید.")
            return

        try:
            price = int(offer_price.text.replace(",", "").replace(" ", ""))
            if price <= 0:
                raise ValueError
        except Exception as e:
            await message.reply(
                f"❗️ لطفاً یک عدد معتبر وارد کنید.\n\n"
                f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
            )
            return await offer_handler(client, message, offer, user_id=user_id, chat_id=chat_id)

        turn_all_offers_false()
        # استفاده از نگاشت برای فعال‌سازی کلید صحیح
        offer_key = OFFER_LABELS_MAP.get(offer, offer)
        able_offers[offer_key] = True
        price_offers[offer_key] = price
        await message.reply(f"✅ قیمت {offer} با موفقیت به {toman_form(price)} تغییر یافت.")
        await special_offer(
            client,
            message,
            user_id or (getattr(message, "from_user", None) and message.from_user.id),
            chat_id or (getattr(message, "chat", None) and message.chat.id)
        )
    except Exception as e:
        logging.error(f"[offer_handler] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی در ثبت قیمت رخ داد. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
            f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        )

async def offer_finalize(client, message, user_id, chat_id):
    """
    نهایی کردن قیمت‌های ویژه و ارسال به کانال
    """
    try:
        try:
            # Patch: Ensure offer_pic_generator has correct datetime
            import sys
            import datetime as _real_datetime
            offer_pic_mod = None
            if ".offer_pic_generator" in sys.modules:
                offer_pic_mod = sys.modules[".offer_pic_generator"]
            elif "plugins.offer_pic_generator" in sys.modules:
                offer_pic_mod = sys.modules["plugins.offer_pic_generator"]
            if offer_pic_mod and not hasattr(offer_pic_mod, "datetime"):
                offer_pic_mod.datetime = _real_datetime

            state = get_state()
            if state is None:
                await message.reply("❌ هیچ آفر فعالی موجود نیست. لطفاً ابتدا یک آفر ویژه فعال کنید.")
                return
            
            offer_draw(state)
            image_path = Path(getcwd()) / f"./assets/offer{state}.png"
            await message.reply_photo(image_path, caption=MAIN_TEXT)
        except Exception as e:
            logging.error(f"[offer_finalize:draw] {e}\n{traceback.format_exc()}")
            await message.reply(
                f"⏳ لطفاً شکیبا باشید، در حال آماده‌سازی قیمت‌ها هستیم...\n\n"
                f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
            )
            return

        ask_msg = await client.send_message(
            admin_id[0],
            text="آیا از نهایی‌سازی قیمت‌های ویژه اطمینان دارید؟",
            reply_markup=get_confirm_keyboard()
        )
        response = await client.listen(chat_id=admin_id[1], user_id=admin_id[0])

        if not response or not hasattr(response, "text"):
            await client.send_message(admin_id[0], text="⏪ ورودی نامعتبر بود. عملیات لغو شد.")
            return

        if response.text == CONFIRM_LABEL:
            try:
                # Patch: Ensure offer_pic_generator has correct datetime
                import sys
                import datetime as _real_datetime
                offer_pic_mod = None
                if ".offer_pic_generator" in sys.modules:
                    offer_pic_mod = sys.modules[".offer_pic_generator"]
                elif "plugins.offer_pic_generator" in sys.modules:
                    offer_pic_mod = sys.modules["plugins.offer_pic_generator"]
                if offer_pic_mod and not hasattr(offer_pic_mod, "datetime"):
                    offer_pic_mod.datetime = _real_datetime

                state = get_state()
                if state is None:
                    await client.send_message(admin_id[0], "❌ هیچ آفر فعالی موجود نیست. لطفاً ابتدا یک آفر ویژه فعال کنید.")
                    return
                
                offer_draw(state)
                image_path = Path(getcwd()) / f"./assets/offer{state}.png"
                await client.send_photo(CHANNEL_ID, image_path, caption=MAIN_TEXT)
                await client.delete_messages(admin_id[0], [response.id, ask_msg.id])
                await client.send_message(
                    admin_id[0],
                    text=f"🎉 قیمت‌های ویژه با موفقیت نهایی و به کانال ارسال شد {emoji.SPARKLES}"
                )
            except Exception as e:
                logging.error(f"[offer_finalize:send_photo] {e}\n{traceback.format_exc()}")
                await client.send_message(
                    admin_id[0],
                    text=f"❌ خطا در ارسال به کانال. لطفاً بعداً تلاش کنید.\n\n"
                         f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
                )
        elif response.text == DECLINE_LABEL:
            await client.delete_messages(admin_id[0], ask_msg.id)
            await client.send_message(admin_id[0], text="⏪ تغییرات ذخیره نشد و به منوی ویژه بازگشتید.")
        else:
            await client.send_message(admin_id[0], text="⏪ گزینه نامعتبر بود. عملیات لغو شد.")
    except Exception as e:
        logging.error(f"[offer_finalize] {e}\n{traceback.format_exc()}")
        await message.reply(
            f"❌ خطایی در نهایی‌سازی قیمت‌ها رخ داد. لطفاً مجدداً تلاش کنید یا با پشتیبانی تماس بگیرید.\n\n"
            f"🔎 جزییات خطا:\n<code>{e}</code>\n<code>{traceback.format_exc()}</code>"
        )

# ================== TEST MODE ==================
if __name__ == "__main__":
    # حالت تستی: وقتی این فایل مستقیماً اجرا شود، همه قیمت‌ها را روی 128000 می‌گذارد و بنرها را تولید می‌کند
    import time

    # لیست کلیدهای آفر (بدون ایموجی)
    offer_keys = [
        "خرید ویژه نقدی",
        "خرید ویژه از حساب",
        "خرید ویژه تتر",
        "فروش ویژه نقدی",
        "فروش ویژه از حساب",
        "فروش ویژه تتر",
    ]
    # همه آفرها فعال و قیمت تستی
    for k in offer_keys:
        able_offers[k] = True
        price_offers[k] = 128000

    # تابع تستی برای تولید همه بنرها
    def test_generate_all_banners():
        print("در حال تولید بنرهای تستی با قیمت 128000 ...")
        for idx, k in enumerate(offer_keys, 1):
            try:
                # فرض بر این است که state همان ایندکس است (یا هر مقدار مورد نیاز offer_draw)
                offer_draw(idx)
                image_path = Path(getcwd()) / f"./assets/offer{idx}.png"
                if image_path.exists():
                    print(f"✅ بنر {k} ساخته شد: {image_path}")
                else:
                    print(f"❌ بنر {k} ساخته نشد!")
            except Exception as e:
                print(f"❌ خطا در ساخت بنر {k}: {e}")
                import traceback
                print(traceback.format_exc())
            time.sleep(0.5)
        print("تمام بنرهای تستی ساخته شدند.")

    test_generate_all_banners()
