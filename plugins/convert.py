from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from .data import prices, tether_price, toman_form
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
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text) for text in row] for row in CONVERT_OPTIONS],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True
    )

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
        # استخراج نوع تبدیل بدون ایموجی
        clean_type = conversion_type[1:].strip()
        
        if "تومن به" in clean_type:
            msg = await client.send_message(
                message.chat.id,
                "✨ لطفاً مبلغ تومانی را وارد کنید:",
                reply_markup=ReplyKeyboardRemove()
            )
            
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
            msg = await client.send_message(
                message.chat.id,
                f"✨ لطفاً مبلغ {currency} را وارد کنید:",
                reply_markup=ReplyKeyboardRemove()
            )
            
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
        
        # ارسال نتیجه با افکت شیشه‌ای
        await message.reply(
            f"""
            ╔════════════════════════╗
            ║    نتیجه تبدیل ارز     ║
            ╠════════════════════════╣
            ║                        
            ║  {symbol} {amount:,.0f} → {result:,.2f}
            ║                        
            ║  نرخ تبدیل: {toman_form(rate)} 
            ║                        
            ╚════════════════════════╝
            """,
            reply_markup=get_glass_keyboard()
        )
        
    except asyncio.TimeoutError:
        await message.reply("⏳ زمان پاسخگویی به پایان رسید. لطفاً دوباره تلاش کنید.",
                          reply_markup=get_glass_keyboard())
    except ValueError as ve:
        await message.reply(f"⚠️ {ve}", reply_markup=get_glass_keyboard())
    except Exception as e:
        await message.reply(f"❌ خطا در محاسبه: {str(e)}",
                          reply_markup=get_glass_keyboard())

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
        await show_glass_panel(client, message)