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
    await client.send_message(id_of_chat, text=ask)

    news = await client.listen(id_of_chat)

    side_text = """
🔺🔺🔺🔺🔺🔺🔺🔺🔺
Mr. Mahdi    📞  +447533544249

Ms. Kianian    📞  +989121894230

Manager  📞  +447399990340
🔺🔺🔺🔺🔺🔺🔺🔺🔺
📌 آدرس دفتر:
<u>Office No7
708A High Road
North Finchley
N12 9QL</u>

🔘 ساعات کاری:
دوشنبه تا جمعه: 🕤 ۹:۳۰ تا 🕠 ۱۷:۳۰
شنبه‌ها: 🕥 ۱۰:۳۰ تا 🕝 ۱۴:۳۰
🔺🔺🔺🔺🔺🔺🔺🔺🔺
"""

    text = f"{news.text.strip()}\n\n{side_text.strip()}"

    try:
        add_date_to_news()
        data_folder = Path(getcwd())
        image_to_open = data_folder / "./assets/news_date.png"
        await message.reply_photo(image_to_open, caption=text)
    except Exception:
        await message.reply("⏳ لطفاً شکیبا باشید، تصویر اعلان در حال آماده‌سازی است...")

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

    ask_user = await client.send_message(
        admin_id[0],
        text="آیا مایل به انتشار این اعلان هستید؟",
        reply_markup=yes_or_no
    )

    response = await client.listen(chat_id=admin_id[0], user_id=admin_id[1])

    if response.text == "✅ بله، منتشر کن":
        add_date_to_news()
        data_folder = Path(getcwd())
        image_to_open = data_folder / "./assets/news_date.png"

        await client.send_photo(CHANNEL_ID, image_to_open, caption=text)
        await client.delete_messages(admin_id[0], [response.id, ask_user.id])
        await client.send_message(
            admin_id[0],
            text=f"✅ اعلان شما با موفقیت منتشر شد! {emoji.THUMBS_UP_LIGHT_SKIN_TONE}"
        )

    elif response.text == "🔄 خیر، نیاز به ویرایش دارم":
        await client.delete_messages(admin_id[0], ask_user.id)
        await client.send_message(
            admin_id[0],
            text="🔄 اعلان منتشر نشد. هر زمان آماده بودید، می‌توانید مجدداً اقدام کنید."
        )

