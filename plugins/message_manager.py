# ===================== Imports =====================
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyromod import Client
import asyncio

# ===================== Message Management =====================

class MessageManager:
    """مدیریت پیام‌ها و دکمه‌های بازگشت"""
    
    def __init__(self):
        self.user_messages = {}  # {user_id: [message_ids]}
    
    async def add_message(self, user_id: int, message_id: int):
        """اضافه کردن پیام به لیست پیام‌های کاربر"""
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id].append(message_id)
    
    async def cleanup_user_messages(self, client: Client, user_id: int, chat_id: int):
        """حذف تمام پیام‌های قبلی کاربر"""
        if user_id in self.user_messages:
            for msg_id in self.user_messages[user_id]:
                try:
                    await client.delete_messages(chat_id, msg_id)
                except Exception:
                    pass  # پیام ممکن است قبلاً حذف شده باشد
            self.user_messages[user_id] = []
    
    async def send_clean_message(self, client: Client, chat_id: int, text: str, 
                               reply_markup=None, user_id: int = None):
        """ارسال پیام جدید و حذف پیام‌های قبلی"""
        if user_id:
            await self.cleanup_user_messages(client, user_id, chat_id)
        
        message = await client.send_message(chat_id, text, reply_markup=reply_markup)
        
        if user_id:
            await self.add_message(user_id, message.id)
        
        return message

# ===================== Back Button Utilities =====================

def get_back_button(callback_data: str = "back_to_main", text: str = "🔙 بازگشت"):
    """ایجاد دکمه بازگشت"""
    return InlineKeyboardButton(text, callback_data=callback_data)

def get_home_button():
    """ایجاد دکمه بازگشت به خانه"""
    return InlineKeyboardButton("🏠 بازگشت به خانه", callback_data="back_to_home")

def add_back_button_to_keyboard(keyboard: list, callback_data: str = "back_to_main", 
                               text: str = "🔙 بازگشت"):
    """اضافه کردن دکمه بازگشت به کیبورد موجود"""
    if keyboard and isinstance(keyboard[-1], list):
        keyboard[-1].append(get_back_button(callback_data, text))
    else:
        keyboard.append([get_back_button(callback_data, text)])
    return keyboard

# ===================== Global Message Manager Instance =====================
message_manager = MessageManager()

# ===================== Back Button Handlers =====================

@Client.on_callback_query("back_to_home")
async def back_to_home_handler(client, callback_query):
    """بازگشت به منوی اصلی"""
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # ارسال منوی اصلی
    welcome_text = (
        f"🏠 به صرافی پردیس خوش آمدید!\n\n"
        "از اینکه ما را برای خدمات ارزی انتخاب کردید سپاسگزاریم.\n"
        "در این ربات می‌توانید به راحتی و با اطمینان ارزهای خود را تبدیل کنید و از قیمت‌های لحظه‌ای مطلع شوید.\n\n"
        f"💰 برای ورود به تبدیل‌کننده ارز، روی دکمه زیر کلیک کنید:"
    )
    
    converter_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("💱 ورود به تبدیل‌کننده", callback_data="open_converter_panel")]
    ])
    
    await message_manager.send_clean_message(
        client, chat_id, welcome_text, converter_button, user_id
    )

@Client.on_callback_query("back_to_main")
async def back_to_main_handler(client, callback_query):
    """بازگشت به منوی اصلی تبدیل‌کننده"""
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # ارسال منوی تبدیل‌کننده
    from .convert import get_glass_keyboard, get_glass_price_text
    
    text = (
        f"💱 قیمت‌های لحظه‌ای بازار:\n"
        f"{get_glass_price_text()}\n"
        f"لطفاً یکی از گزینه‌های زیر را برای تبدیل ارز انتخاب کنید:"
    )
    
    await message_manager.send_clean_message(
        client, chat_id, text, get_glass_keyboard(), user_id
    )

@Client.on_callback_query("back_to_admin")
async def back_to_admin_handler(client, callback_query):
    """بازگشت به پنل ادمین"""
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    # ارسال پنل ادمین
    from .admin_panel import admin_panel
    await admin_panel(client, callback_query.message, user_id, chat_id)
