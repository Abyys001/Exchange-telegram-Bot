# ===================== Imports =====================
from pyrogram.errors import UserNotParticipant
from .data import CHANNEL_ID, ADMINS

# ===================== Filters =====================

async def check_member(_, client, message):
    """بررسی عضویت کاربر در کانال"""
    user_id = getattr(message.from_user, "id", None)
    if not user_id:
        return False

    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        if member.status in {"member", "administrator", "creator"}:
            return True
    except UserNotParticipant:
        text = (
            "👋 خوش آمدید به ربات صرافی پردیس!\n\n"
            "برای استفاده از امکانات ربات، لطفاً ابتدا در کانال زیر عضو شوید و سپس دستور /start را ارسال کنید:\n\n"
            "🔗 [عضویت در کانال](https://t.me/sarafipardis)"
        )
        await client.send_message(user_id, text, disable_web_page_preview=True)
    except Exception as e:
        import logging
        logging.error(f"[check_member] Error: {e}")
    return False

async def not_admin(_, client, message):
    """بررسی اینکه کاربر ادمین نباشد"""
    user_id = getattr(message.from_user, "id", None)
    return user_id not in ADMINS if user_id else False
