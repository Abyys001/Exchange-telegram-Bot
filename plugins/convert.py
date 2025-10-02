from pyrogram.types import (
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from .data import prices, tether_price, toman_form
from .message_manager import message_manager, get_back_button, get_home_button
import asyncio
from pyromod import Client
from pyrogram import filters

# ===================== Constants =====================
CONVERT_OPTIONS = [
    ["💵 تومن به پوند نقدی", "💳 تومن به پوند حسابی"],
    ["💷 پوند نقدی به تومن", "🏦 پوند حسابی به تومن"],
    ["💲 تومن به تتر", "🔁 تتر به تومن"],
    ["⭐ تومن به پوند ویژه", "🌟 پوند ویژه به تومن"],
    ["🔙 بازگشت به منوی اصلی"]
]

# ایجاد لیست صاف شده از تمام گزینه‌های معتبر
ALL_VALID_OPTIONS = [option[1:] for row in CONVERT_OPTIONS for option in row]  # حذف ایموجی برای تطابق بهتر

# ===================== Helper Functions =====================
def get_glass_keyboard():
    """Create modern glassmorphism keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💵 تومن به پوند نقدی", callback_data="convert_toman_to_cash_pound"),
            InlineKeyboardButton("💳 تومن به پوند حسابی", callback_data="convert_toman_to_account_pound")
        ],
        [
            InlineKeyboardButton("💷 پوند نقدی به تومن", callback_data="convert_cash_pound_to_toman"),
            InlineKeyboardButton("🏦 پوند حسابی به تومن", callback_data="convert_account_pound_to_toman")
        ],
        [
            InlineKeyboardButton("💲 تومن به تتر", callback_data="convert_toman_to_tether"),
            InlineKeyboardButton("🔁 تتر به تومن", callback_data="convert_tether_to_toman")
        ],
        [
            InlineKeyboardButton("⭐ تومن به پوند ویژه", callback_data="convert_toman_to_special_pound"),
            InlineKeyboardButton("🌟 پوند ویژه به تومن", callback_data="convert_special_pound_to_toman")
        ],
        [get_home_button()]
    ])

def get_glass_price_text():
    """Generate stylish price information"""
    price_text = """
╔════════════════════════╗
║      قیمت‌های لحظه‌ای      ║
╠════════════════════════╣
║                        
║  💵 خرید پوند نقدی: {cash_buy}
║  💳 خرید پوند حسابی: {acc_buy}
║  💸 فروش پوند نقدی: {cash_sell}
║  🏦 فروش پوند حسابی: {acc_sell}
║  ⭐ پوند ویژه: {special}
║                        
╠════════════════════════╣
║  💰 خرید تتر: {usdt_buy}
║  🔄 فروش تتر: {usdt_sell}
║                        
╚════════════════════════╝
""".format(
        cash_buy=toman_form(prices.get("cash_purchase_price", "0")),
        acc_buy=toman_form(prices.get("buy_from_account", "0")),
        cash_sell=toman_form(prices.get("cash_sales_price", "0")),
        acc_sell=toman_form(prices.get("sell_from_account", "0")),
        special=toman_form(prices.get("offical_sale_price", "0")),
        usdt_buy=toman_form(tether_price.get("tether_buy_irr", 0)),
        usdt_sell=toman_form(tether_price.get("tether_sell_irr", 0))
    )
    return price_text

# ===================== Price Access Helpers =====================
def get_price(price_type):
    """دریافت قیمت از دیکشنری prices با هندل خطا"""
    try:
        value = prices.get(price_type)
        if value is None:
            raise ValueError(f"قیمت '{price_type}' یافت نشد.")
        # Remove commas before converting to float
        if isinstance(value, str):
            value = value.replace(",", "")
        return float(value)
    except Exception as e:
        raise ValueError(f"خطا در دریافت قیمت: {e}")

def get_tether_price(is_buy=True):
    """دریافت قیمت تتر خرید یا فروش"""
    try:
        key = "tether_buy_irr" if is_buy else "tether_sell_irr"
        value = tether_price.get(key)
        if value is None:
            raise ValueError(f"قیمت تتر '{key}' یافت نشد.")
        # Remove commas before converting to float
        if isinstance(value, str):
            value = value.replace(",", "")
        return float(value)
    except Exception as e:
        raise ValueError(f"خطا در دریافت قیمت تتر: {e}")

# ===================== Glass Conversion Handlers =====================
async def handle_glass_conversion(client, message, conversion_type):
    """Modern conversion handler with glass effect"""
    try:
        user_id = message.from_user.id if hasattr(message, 'from_user') else None
        chat_id = message.chat.id
        
        # استخراج نوع تبدیل بدون ایموجی
        clean_type = conversion_type[1:].strip()
        
        if "تومن به" in clean_type:
            # حذف پیام‌های قبلی
            if user_id:
                await message_manager.cleanup_user_messages(client, user_id, chat_id)
            
            msg = await client.send_message(
                message.chat.id,
                "✨ لطفاً مبلغ تومانی را وارد کنید:",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # اضافه کردن پیام به مدیریت
            if user_id:
                await message_manager.add_message(user_id, msg.id)
            
            response = await client.ask(
                message.chat.id,
                "مثال: 1000000",
                reply_to_message_id=msg.id,
                timeout=60
            )
            
            amount = float(response.text.replace(",", ""))
            
            if "پوند نقدی" in clean_type:
                rate = get_price("cash_purchase_price")
                symbol = "💵"
            elif "پوند حسابی" in clean_type:
                rate = get_price("buy_from_account")
                symbol = "💳"
            elif "پوند ویژه" in clean_type:
                rate = get_price("offical_sale_price")
                symbol = "⭐"
            elif "تتر" in clean_type:
                rate = get_tether_price(is_buy=True)
                symbol = "💲"
            else:
                raise ValueError("نوع تبدیل نامعتبر است.")
                
            result = amount / rate
            
        elif "به تومن" in clean_type:
            currency = "پوند" if "پوند" in clean_type else "تتر"
            
            # حذف پیام‌های قبلی
            if user_id:
                await message_manager.cleanup_user_messages(client, user_id, chat_id)
            
            msg = await client.send_message(
                message.chat.id,
                f"✨ لطفاً مبلغ {currency} را وارد کنید:",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # اضافه کردن پیام به مدیریت
            if user_id:
                await message_manager.add_message(user_id, msg.id)
            
            response = await client.ask(
                message.chat.id,
                f"مثال: 100 {currency}",
                reply_to_message_id=msg.id,
                timeout=60
            )
            
            amount = float(response.text.replace(",", ""))
            
            if "پوند نقدی" in clean_type:
                rate = get_price("cash_sales_price")
                symbol = "💷"
            elif "پوند حسابی" in clean_type:
                rate = get_price("sell_from_account")
                symbol = "🏦"
            elif "پوند ویژه" in clean_type:
                rate = get_price("offical_sale_price")
                symbol = "🌟"
            elif "تتر" in clean_type:
                rate = get_tether_price(is_buy=False)
                symbol = "🔁"
            else:
                raise ValueError("نوع تبدیل نامعتبر است.")
                
            result = amount * rate
        
        else:
            raise ValueError("نوع تبدیل شناسایی نشد.")
        
        # حذف پیام‌های قبلی و ارسال نتیجه
        if user_id:
            await message_manager.cleanup_user_messages(client, user_id, chat_id)
        
        result_text = f"""
        ╔════════════════════════╗
        ║    نتیجه تبدیل ارز     ║
        ╠════════════════════════╣
        ║                        
        ║  {symbol} {amount:,.0f} → {result:,.2f}
        ║                        
        ║  نرخ تبدیل: {toman_form(rate)} 
        ║                        
        ╚════════════════════════╝
        """
        
        await message_manager.send_clean_message(
            client, chat_id, result_text, get_glass_keyboard(), user_id
        )
        
    except asyncio.TimeoutError:
        if user_id:
            await message_manager.cleanup_user_messages(client, user_id, chat_id)
        await message_manager.send_clean_message(
            client, chat_id, 
            "⏳ زمان پاسخگویی به پایان رسید. لطفاً دوباره تلاش کنید.",
            get_glass_keyboard(), user_id
        )
    except ValueError as ve:
        if user_id:
            await message_manager.cleanup_user_messages(client, user_id, chat_id)
        await message_manager.send_clean_message(
            client, chat_id, f"⚠️ {ve}", get_glass_keyboard(), user_id
        )
    except Exception as e:
        if user_id:
            await message_manager.cleanup_user_messages(client, user_id, chat_id)
        await message_manager.send_clean_message(
            client, chat_id, f"❌ خطا در محاسبه: {str(e)}", get_glass_keyboard(), user_id
        )

# ===================== Main Glass Handlers =====================
async def show_glass_panel(client, message):
    """Show glassmorphism converter panel"""
    await message.reply(
        get_glass_price_text(),
        reply_markup=get_glass_keyboard()
    )

@Client.on_message(filters.command(["convert", "تبدیل"]))
async def start_glass_converter(client, message):
    """Start glass converter"""
    await show_glass_panel(client, message)

# ===================== Convert Callback Handlers =====================

@Client.on_callback_query(filters.regex("^convert_toman_to_cash_pound$"))
async def convert_toman_to_cash_pound_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "💵 تومن به پوند نقدی")

@Client.on_callback_query(filters.regex("^convert_toman_to_account_pound$"))
async def convert_toman_to_account_pound_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "💳 تومن به پوند حسابی")

@Client.on_callback_query(filters.regex("^convert_cash_pound_to_toman$"))
async def convert_cash_pound_to_toman_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "💷 پوند نقدی به تومن")

@Client.on_callback_query(filters.regex("^convert_account_pound_to_toman$"))
async def convert_account_pound_to_toman_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "🏦 پوند حسابی به تومن")

@Client.on_callback_query(filters.regex("^convert_toman_to_tether$"))
async def convert_toman_to_tether_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "💲 تومن به تتر")

@Client.on_callback_query(filters.regex("^convert_tether_to_toman$"))
async def convert_tether_to_toman_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "🔁 تتر به تومن")

@Client.on_callback_query(filters.regex("^convert_toman_to_special_pound$"))
async def convert_toman_to_special_pound_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "⭐ تومن به پوند ویژه")

@Client.on_callback_query(filters.regex("^convert_special_pound_to_toman$"))
async def convert_special_pound_to_toman_handler(client, callback_query):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    # حذف پیام‌های قبلی
    await message_manager.cleanup_user_messages(client, user_id, chat_id)
    
    await handle_glass_conversion(client, callback_query.message, "🌟 پوند ویژه به تومن")

@Client.on_message(filters.text & filters.private)
async def handle_glass_messages(client, message):
    """Handle glass converter selections"""
    user_input = message.text.strip()
    
    # بررسی تطابق با حذف ایموجی
    clean_input = user_input[1:] if user_input and user_input[0] in ["💵","💳","💷","🏦","💲","🔁","⭐","🌟","🔙"] else user_input
    
    if any(option in clean_input for option in ALL_VALID_OPTIONS):
        if "بازگشت" in clean_input:
            await message.reply("✅ به منوی اصلی بازگشتید.", 
                              reply_markup=ReplyKeyboardRemove())
            return
            
        await handle_glass_conversion(client, message, user_input)
        # حذف این خط که باعث infinite loop می‌شود
        # await show_glass_panel(client, message)