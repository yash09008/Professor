# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Clone Code Credit : YT - @Tech_VJ / TG - @VJ_Bots / GitHub - @VJBots

import sys
import glob
import importlib
import logging
import logging.config
import pytz
import asyncio
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, idle
from pyrogram.errors import FloodWait
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server
from plugins.clone import restart_bots

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

# Import premium database
from database.premium_db import premium_db

class Bot:
    def __init__(self):
        self.techvj_bot = TechVJBot
        self.is_restarting = False
        
    async def start_bot(self):
        """Main method to start the bot"""
        try:
            print('\n')
            print('=' * 50)
            print('🚀 Starting Premium FSUB Bot')
            print('=' * 50)
            
            # First start TechVJBot asynchronously
            await self.start_techvj_bot()
            
            # Get bot info
            bot_info = await self.techvj_bot.get_me()
            logging.info(f"Bot Started as @{bot_info.username}")
            
            # Initialize premium database system
            await self.initialize_premium_system()
            
            # Initialize clients
            await initialize_clients()
            
            # Load plugins
            await self.load_plugins()
            
            # Start ping server task on Heroku
            if ON_HEROKU:
                asyncio.create_task(ping_server())
            
            # Load banned data with error handling
            await self.load_banned_data()
            
            # Store bot info
            await self.store_bot_info()
            
            # Logging info
            logging.info(script.LOGO)
            
            # Send status messages
            await self.send_status_messages()
            
            # Restart clone bots if enabled
            if CLONE_MODE:
                await self.restart_clone_bots()
            
            # Start web server
            await self.start_web_server()
            
            # Print bot information
            await self.print_bot_info(bot_info)
            
            # Keep bot in idle state
            await idle()
            
        except FloodWait as e:
            wait_time = e.value
            logging.error(f"FloodWait Error: Wait for {wait_time} seconds")
            print(f"\n⚠️ FloodWait Error!")
            print(f"⏳ Please wait for {wait_time} seconds ({wait_time/60:.1f} minutes)")
            print(f"🕒 Bot will automatically start after wait time")
            
            # Sleep for wait time
            await asyncio.sleep(wait_time)
            
            # Try to start again
            if not self.is_restarting:
                self.is_restarting = True
                await self.start_bot()
                
        except Exception as e:
            logging.error(f"Error starting bot: {e}")
            print(f"\n❌ Error: {e}")
            print("Please check your configuration and try again.")
            raise
    
    async def initialize_premium_system(self):
        """Initialize premium and FSUB systems"""
        try:
            # Reset daily usage data
            await premium_db.reset_daily_usage()
            print("✅ Premium system initialized")
            
            # Check FSUB channels configuration
            if len(FSUB_CHANNELS) < 4:
                print(f"⚠️ WARNING: Only {len(FSUB_CHANNELS)} FSUB channels configured")
                print("ℹ️ Bot requires 4 channels for FSUB system")
            else:
                print(f"✅ FSUB System: {len(FSUB_CHANNELS)} channels configured")
            
            # Print system status
            print(f"⭐ Premium System: {'ENABLED' if PREMIUM_ENABLED else 'DISABLED'}")
            print(f"🎯 Daily Free Limit: {DAILY_FREE_LIMIT} files")
            print(f"🔗 Unique Links: {'ENABLED' if UNIQUE_LINK_ENABLED else 'DISABLED'}")
            print(f"👑 Admins: {len(ADMINS)}")
            
        except Exception as e:
            logging.error(f"Error initializing premium system: {e}")
            print("⚠️ Error initializing premium system")
    
    async def start_techvj_bot(self):
        """Start TechVJBot asynchronously"""
        try:
            # Check if bot is already running
            if not self.techvj_bot.is_connected:
                await self.techvj_bot.start()
                print("✅ TechVJBot started successfully")
            else:
                print("ℹ️ TechVJBot is already running")
        except FloodWait as e:
            # Pass FloodWait error up
            raise
        except Exception as e:
            logging.error(f"Error starting TechVJBot: {e}")
            raise
    
    async def load_plugins(self):
        """Load all plugins"""
        ppath = "plugins/*.py"
        files = glob.glob(ppath)
        
        print(f"\n📂 Loading Plugins...")
        loaded_count = 0
        
        for file_path in files:
            try:
                plugin_path = Path(file_path)
                plugin_name = plugin_path.stem
                
                # Skip __pycache__ and __init__ files
                if plugin_name.startswith("__"):
                    continue
                    
                import_path = f"plugins.{plugin_name}"
                
                # Import plugin
                spec = importlib.util.spec_from_file_location(import_path, plugin_path)
                if spec is None:
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[import_path] = module
                
                # Initialize FSUB manager if it's the fsub plugin
                if plugin_name == "fsub":
                    from plugins.fsub import setup_fsub
                    setup_fsub(self.techvj_bot)
                    print(f"✅ Imported & Initialized: {plugin_name}")
                else:
                    print(f"✅ Imported: {plugin_name}")
                
                loaded_count += 1
                
            except Exception as e:
                print(f"❌ Error loading plugin {plugin_name}: {e}")
        
        print(f"📊 Total plugins loaded: {loaded_count}")
        
        # Check for required plugins
        required_plugins = ["fsub", "premium", "unique_links"]
        for req_plugin in required_plugins:
            plugin_file = Path(f"plugins/{req_plugin}.py")
            if not plugin_file.exists():
                print(f"⚠️ WARNING: Required plugin '{req_plugin}.py' not found")
    
    async def load_banned_data(self):
        """Load banned users and chats with MongoDB error handling"""
        try:
            # Try to get banned data
            b_users, b_chats = await db.get_banned()
            temp.BANNED_USERS = b_users
            temp.BANNED_CHATS = b_chats
            print(f"✅ Loaded {len(b_users)} banned users and {len(b_chats)} banned chats")
            
        except Exception as e:
            logging.error(f"Error loading banned data: {e}")
            print(f"⚠️ MongoDB Connection Error: {e}")
            print("⚠️ Using empty banned lists for now...")
            
            # Set empty lists if database connection fails
            temp.BANNED_USERS = []
            temp.BANNED_CHATS = []
            
            # Check if it's SSL error
            if "SSL" in str(e) or "TLS" in str(e):
                print("\n🔧 SSL/TLS Certificate Error Detected!")
                print("Solution: Add 'ssl=false' to your MongoDB connection string in info.py")
    
    async def store_bot_info(self):
        """Store bot information"""
        try:
            me = await self.techvj_bot.get_me()
            temp.BOT = self.techvj_bot
            temp.ME = me.id
            temp.U_NAME = me.username
            temp.B_NAME = me.first_name
            print(f"✅ Bot info stored: @{me.username}")
        except Exception as e:
            logging.error(f"Error storing bot info: {e}")
            print("❌ Error storing bot info")
    
    async def send_status_messages(self):
        """Send restart status messages"""
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        
        print(f"\n📨 Sending status messages...")
        
        # Send to log channel
        if LOG_CHANNEL:
            try:
                await self.techvj_bot.send_message(
                    chat_id=LOG_CHANNEL, 
                    text=script.RESTART_TXT.format(today, time)
                )
                print(f"✅ Status sent to log channel: {LOG_CHANNEL}")
            except Exception as e:
                logging.error(f"Error sending message to log channel: {e}")
                print("❌ Make Your Bot Admin In Log Channel With Full Rights")
        
        # Send to channels
        if CHANNELS:
            for ch in CHANNELS:
                try:
                    k = await self.techvj_bot.send_message(
                        chat_id=ch, 
                        text="**Bot Restarted**\n\n⚠️ New Features Added:\n• 4-Channel FSUB System\n• Premium & Referral System\n• Unique Link Generator\n• Daily Download Limits"
                    )
                    await k.delete()
                    print(f"✅ Status sent to channel: {ch}")
                except Exception as e:
                    logging.error(f"Error sending message to channel {ch}: {e}")
                    print(f"❌ Make Your Bot Admin In Channel {ch} With Full Rights")
        
        # Send to auth channel
        if AUTH_CHANNEL:
            try:
                k = await self.techvj_bot.send_message(
                    chat_id=AUTH_CHANNEL, 
                    text="**Bot Restarted**\n\n⚠️ FSUB System Active\nUsers must join all 4 channels"
                )
                await k.delete()
                print(f"✅ Status sent to auth channel: {AUTH_CHANNEL}")
            except Exception as e:
                logging.error(f"Error sending message to auth channel: {e}")
                print("❌ Make Your Bot Admin In Force Subscribe Channel With Full Rights")
    
    async def restart_clone_bots(self):
        """Restart clone bots"""
        try:
            print("\n🔄 Restarting All Clone Bots...")
            await restart_bots()
            print("✅ Restarted All Clone Bots.")
        except Exception as e:
            logging.error(f"Error restarting clone bots: {e}")
            print("❌ Error restarting clone bots")
    
    async def start_web_server(self):
        """Start web server"""
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, PORT).start()
            logging.info(f"Web server started on port {PORT}")
            print(f"🌐 Web server started on port {PORT}")
        except Exception as e:
            logging.error(f"Error starting web server: {e}")
            print("❌ Error starting web server")
    
    async def print_bot_info(self, bot_info):
        """Print bot information"""
        print("\n" + "=" * 50)
        print("✅ Bot Successfully Started!")
        print("=" * 50)
        print(f"🤖 Bot Username: @{bot_info.username}")
        print(f"👤 Bot Name: {bot_info.first_name}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print(f"🌐 Session: {SESSION}")
        
        # System Features
        print("\n📊 SYSTEM FEATURES:")
        print(f"   • 4-Channel FSUB: {'✅' if len(FSUB_CHANNELS) >= 4 else '⚠️'}")
        print(f"   • Premium System: {'✅' if PREMIUM_ENABLED else '❌'}")
        print(f"   • Daily Limit: {DAILY_FREE_LIMIT} files")
        print(f"   • Unique Links: {'✅' if UNIQUE_LINK_ENABLED else '❌'}")
        print(f"   • Referral System: {'✅' if REFERRAL_ENABLED else '❌'}")
        
        # Channel Info
        print(f"\n📢 CHANNELS:")
        print(f"   • FSUB Channels: {len(FSUB_CHANNELS)}")
        print(f"   • File Channel: {FILE_CHANNEL}")
        print(f"   • Log Channel: {LOG_CHANNEL}")
        
        # Admin Info
        print(f"\n👑 ADMINISTRATORS:")
        print(f"   • Total Admins: {len(ADMINS)}")
        if ADMINS:
            print(f"   • Primary Admin: {ADMINS[0]}")
        
        print("\n" + "=" * 50)
        print("💡 Bot is now ready to use!")
        print("💡 Use /start to test FSUB system")
        print("💡 Admins can use /getlink to generate unique links")
        print("=" * 50)

async def main():
    """Main async function"""
    bot = Bot()
    await bot.start_bot()

if __name__ == '__main__':
    try:
        # Get event loop
        loop = asyncio.get_event_loop()
        
        # Run main function
        loop.run_until_complete(main())
        
    except KeyboardInterrupt:
        print("\n\n👋 Service Stopped Bye")
        logging.info('Service Stopped Bye 👋')
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
        print("\nPlease check your configuration and try again.")
        print("Common issues:")
        print("1. Check API_ID, API_HASH, and BOT_TOKEN")
        print("2. Check MongoDB connection string")
        print("3. Ensure bot is admin in all channels")
        print("4. Check environment variables")