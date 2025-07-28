from pathlib import Path
from os import getcwd
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
from pyrogram import emoji

from .data import admin_id, CHANNEL_ID
from .offer_pic_generator import add_date_to_news

# ============== NEWS HANDLER ==============

async def news_handler(client, message):
    """
    Handle creating and publishing news announcements.
    """
    id_of_chat = message.chat.id

    ask = "📝 لطفاً متن اعلان مورد نظر خود را با دقت وارد کنید:"
    try:
        await client.send_message(id_of_chat, text=ask)
    except Exception as e:
        await message.reply(f"❌ خطا در ارسال پیام درخواست متن اعلان:\n{e}")
        return

    try:
        news = await client.listen(id_of_chat)
    except Exception as e:
        await message.reply(f"❌ خطا در دریافت متن اعلان:\n{e}")
        return

    side_text = """
🔺🔺🔺🔺🔺🔺🔺🔺🔺
Mr. Mahdi    📞  +447533544249

Ms. Kianian    📞  +989121894230

Manager  📞  +447399990340
🔺🔺🔺🔺🔺🔺🔺🔺🔺
📌 آدرس دفتر:
<u>Office A
708A High Road
North Finchley
N12 9QL</u>

🔘 ساعات کاری:
دوشنبه تا جمعه: 🕤 ۹:۳۰ تا 🕠 ۱۷:۳۰
شنبه‌ها: 🕥 ۱۰:۳۰ تا 🕝 ۱۴:۳۰
🔺🔺🔺🔺🔺🔺🔺🔺🔺
"""

    try:
        news_text = news.text.strip()
    except Exception as e:
        await message.reply(f"❌ خطا در پردازش متن اعلان:\n{e}")
        return

    text = f"{news_text}\n\n{side_text.strip()}"

    # مرحله آماده‌سازی و ارسال عکس پیش‌نمایش
    try:
        add_date_to_news()
        data_folder = Path(getcwd())
        image_to_open = data_folder / "assets" / "news_date.png"
        await message.reply_photo(str(image_to_open), caption=text)
    except Exception as e:
        await message.reply(f"⏳ لطفاً شکیبا باشید، تصویر اعلان در حال آماده‌سازی است...\n\n❌ خطا: {e}")
        return

    yes_or_no = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton("✅ بله، منتشر کن"),
                KeyboardButton("🔄 خیر، نیاز به ویرایش دارم")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    try:
        ask_user = await client.send_message(
            admin_id[0],
            text="آیا مایل به انتشار این اعلان هستید؟",
            reply_markup=yes_or_no
        )
    except Exception as e:
        await message.reply(f"❌ خطا در ارسال پیام تایید انتشار به ادمین:\n{e}")
        return

    try:
        response = await client.listen(chat_id=admin_id[0], user_id=admin_id[1])
    except Exception as e:
        await message.reply(f"❌ خطا در دریافت پاسخ ادمین:\n{e}")
        return

    try:
        if response.text == "✅ بله، منتشر کن":
            try:
                add_date_to_news()
                data_folder = Path(getcwd())
                image_to_open = data_folder / "assets" / "news_date.png"
                await client.send_photo(CHANNEL_ID, str(image_to_open), caption=text)
                await client.delete_messages(admin_id[0], [response.id, ask_user.id])
                await client.send_message(
                    admin_id[0],
                    text=f"✅ اعلان شما با موفقیت منتشر شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}"
                )
            except Exception as e:
                await client.send_message(
                    admin_id[0],
                    text=f"❌ خطا در انتشار اعلان:\n{e}"
                )
                await message.reply(f"❌ خطا در انتشار اعلان:\n{e}")
        elif response.text == "🔄 خیر، نیاز به ویرایش دارم":
            try:
                await client.delete_messages(admin_id[0], ask_user.id)
            except Exception:
                pass
            await client.send_message(
                admin_id[0],
                text="🔄 اعلان منتشر نشد. هر زمان آماده بودید، می‌توانید مجدداً اقدام کنید."
            )
        else:
            await client.send_message(
                admin_id[0],
                text="❗️ پاسخ نامعتبر بود. لطفاً مجدداً اقدام کنید."
            )
    except Exception as e:
        await message.reply(f"❌ خطای غیرمنتظره:\n{e}")

