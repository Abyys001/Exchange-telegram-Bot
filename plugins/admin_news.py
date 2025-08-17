from pathlib import Path
from os import getcwd
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import emoji
from pyromod import Client
from pyrogram import filters

from .data import admin_id, CHANNEL_ID
from .offer_pic_generator import add_date_to_news
from .message_manager import message_manager, get_back_button

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
        add_date_to_news(news_text)
        data_folder = Path(getcwd())
        image_to_open = data_folder / "assets" / "news_date.png"
        await message.reply_photo(str(image_to_open), caption=text)
    except Exception as e:
        await message.reply(f"⏳ لطفاً شکیبا باشید، تصویر اعلان در حال آماده‌سازی است...\n\n❌ خطا: {e}")
        return

    yes_or_no = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ بله، منتشر کن", callback_data="news_publish"),
            InlineKeyboardButton("🔄 خیر، نیاز به ویرایش دارم", callback_data="news_edit")
        ],
        [get_back_button("back_to_admin", "🔙 بازگشت به پنل ادمین")]
    ])

    try:
        ask_user = await client.send_message(
            admin_id[0],
            text="آیا مایل به انتشار این اعلان هستید؟",
            reply_markup=yes_or_no
        )
    except Exception as e:
        await message.reply(f"❌ خطا در ارسال پیام تایید انتشار به ادمین:\n{e}")
        return

# ============== News Callback Handlers ==============

@Client.on_callback_query(filters.regex("^news_publish$"))
async def news_publish_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    try:
        # استخراج متن خبر از caption
        caption = callback_query.message.caption or ""
        # حذف side_text از caption برای استخراج متن خبر اصلی
        side_text_start = caption.find("🔺🔺🔺🔺🔺🔺🔺🔺🔺")
        if side_text_start != -1:
            news_text = caption[:side_text_start].strip()
        else:
            news_text = caption.strip()
        
        add_date_to_news(news_text)
        data_folder = Path(getcwd())
        image_to_open = data_folder / "assets" / "news_date.png"
        await client.send_photo(CHANNEL_ID, str(image_to_open), caption=callback_query.message.caption)
        
        # حذف پیام‌های قبلی و ارسال پیام موفقیت
        await message_manager.cleanup_user_messages(client, user_id, chat_id)
        await message_manager.send_clean_message(
            client, chat_id,
            f"✅ اعلان شما با موفقیت منتشر شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}",
            None, user_id
        )
    except Exception as e:
        await message_manager.cleanup_user_messages(client, user_id, chat_id)
        await message_manager.send_clean_message(
            client, chat_id,
            f"❌ خطا در انتشار اعلان:\n{e}",
            None, user_id
        )

@Client.on_callback_query(filters.regex("^news_edit$"))
async def news_edit_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی و ارسال پیام
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    await message_manager.send_clean_message(
        client, chat_id,
        "🔄 اعلان منتشر نشد. هر زمان آماده بودید، می‌توانید مجدداً اقدام کنید.",
        None, user_id
    )
