import asyncio
from pyrogram import idle
from ARUMUZIC.clients import bot, assistant, call 
import config

async def start_bot():
    print("🚀 Starting ARUMUZIC Clients...")
    
    # Force defining plugins path before start
    bot.plugins = {"root": "ARUMUZIC.plugins"} 
    
    await bot.start()
    await assistant.start()
    await call.start()
    
    print("---------------------------------")
    print("✨ ARUMUZIC IS NOW ONLINE! ✨")
    print("✅ PLUGINS LOADED FROM: ARUMUZIC/plugins")
    print("---------------------------------")
    
    await idle()
    
    await bot.stop()
    await assistant.stop()
    await call.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_bot())
