#!/usr/bin/env python3
"""
Test file for Pardis Bot
"""

import asyncio
from pyromod import Client
from plugins.secret_keys import PARDIS_SECRET_KEY

# Bot configuration
API_ID = 25659111
API_HASH = "2f4d5e01c109e278ac7d29e907647db1"
BOT_TOKEN = PARDIS_SECRET_KEY

async def test_bot():
    """Test the bot functionality"""
    print("Starting bot test...")
    
    app = Client(
        "test_app",
        API_ID,
        API_HASH,
        bot_token=BOT_TOKEN,
    )
    
    try:
        await app.start()
        print("✅ Bot started successfully!")
        print(f"Bot username: @{(await app.get_me()).username}")
        
        # Keep the bot running for a few seconds
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
    finally:
        await app.stop()
        print("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(test_bot()) 