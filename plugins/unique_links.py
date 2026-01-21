import asyncio
import string
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import UNIQUE_LINK_ENABLED, LINK_PREFIX, LINK_LENGTH, ADMINS, FILE_CHANNEL
from database.premium_db import premium_db
from database.users_chats_db import db
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UniqueLinkSystem:
    def __init__(self):
        self.links_db = {}
    
    def generate_unique_code(self, length=10):
        """Generate unique code for link"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    async def create_unique_link(self, file_id, file_name, user_id):
        """Create unique link for file"""
        if not UNIQUE_LINK_ENABLED:
            return None
        
        unique_code = self.generate_unique_code(LINK_LENGTH)
        
        # Store link info
        link_data = {
            "file_id": file_id,
            "file_name": file_name,
            "created_by": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=7),
            "access_count": 0,
            "unique_code": unique_code
        }
        
        # Store in database
        await db.update_unique_link(unique_code, link_data)
        
        # Generate full link
        bot_username = (await Client.get_me()).username
        full_link = f"{LINK_PREFIX}{bot_username}?start=link_{unique_code}"
        
        return full_link, unique_code
    
    async def get_link_info(self, unique_code):
        """Get link information"""
        return await db.get_unique_link(unique_code)
    
    async def track_link_access(self, unique_code, user_id):
        """Track when someone accesses a link"""
        link_data = await self.get_link_info(unique_code)
        if link_data:
            link_data["access_count"] += 1
            link_data["last_accessed"] = datetime.now()
            link_data["last_accessed_by"] = user_id
            await db.update_unique_link(unique_code, link_data)
    
    async def check_link_validity(self, unique_code):
        """Check if link is still valid"""
        link_data = await self.get_link_info(unique_code)
        if not link_data:
            return False, "Link not found"
        
        expires_at = link_data.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        if datetime.now() > expires_at:
            return False, "Link has expired"
        
        return True, "Link is valid"

# Initialize
link_system = UniqueLinkSystem()

@Client.on_message(filters.command("getlink") & filters.private)
async def generate_unique_link(client, message: Message):
    """Generate unique link for file"""
    if not UNIQUE_LINK_ENABLED:
        await message.reply_text("Unique link system is disabled.")
        return
    
    # Check if user has permission
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.reply_text("Only admins can generate unique links.")
        return
    
    # Check if replying to a file
    if not message.reply_to_message or not message.reply_to_message.media:
        await message.reply_text("Please reply to a file to generate a unique link.")
        return
    
    # Get file info
    file = message.reply_to_message
    if file.document:
        file_id = file.document.file_id
        file_name = file.document.file_name
    elif file.video:
        file_id = file.video.file_id
        file_name = file.video.file_name or "video.mp4"
    elif file.audio:
        file_id = file.audio.file_id
        file_name = file.audio.file_name or "audio.mp3"
    else:
        await message.reply_text("Unsupported file type.")
        return
    
    # Generate unique link
    full_link, unique_code = await link_system.create_unique_link(file_id, file_name, user_id)
    
    # Send link to user
    text = f"✅ **Unique Link Generated**\n\n"
    text += f"📁 File: {file_name}\n"
    text += f"🔗 Link: `{full_link}`\n"
    text += f"🆔 Code: `{unique_code}`\n"
    text += f"⏳ Expires: 7 days\n\n"
    text += "Share this link with others!"
    
    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Copy Link", callback_data=f"copy_{full_link}")],
            [InlineKeyboardButton("📤 Share", url=f"https://t.me/share/url?url={full_link}&text=Check%20this%20file!")]
        ])
    )

@Client.on_message(filters.command("linkinfo") & filters.private)
async def link_information(client, message: Message):
    """Get link information"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /linkinfo unique_code")
        return
    
    unique_code = message.command[1]
    link_data = await link_system.get_link_info(unique_code)
    
    if not link_data:
        await message.reply_text("Link not found.")
        return
    
    text = f"🔗 **Link Information**\n\n"
    text += f"📁 File: {link_data.get('file_name', 'Unknown')}\n"
    text += f"👤 Created by: {link_data.get('created_by', 'Unknown')}\n"
    text += f"📅 Created: {link_data.get('created_at', 'Unknown')}\n"
    text += f"⏳ Expires: {link_data.get('expires_at', 'Unknown')}\n"
    text += f"👥 Accessed: {link_data.get('access_count', 0)} times\n"
    
    if link_data.get('last_accessed'):
        text += f"🕒 Last accessed: {link_data.get('last_accessed')}\n"
    
    await message.reply_text(text)

@Client.on_message(filters.command("mylinks") & filters.private)
async def my_links(client, message: Message):
    """Show user's created links"""
    user_id = message.from_user.id
    links = await db.get_user_links(user_id)
    
    if not links:
        await message.reply_text("You haven't created any links yet.")
        return
    
    text = f"📋 **Your Created Links**\n\n"
    
    for link in links[:10]:  # Show first 10 links
        unique_code = link.get("unique_code")
        file_name = link.get("file_name", "Unknown")[:30]
        access_count = link.get("access_count", 0)
        expires_at = link.get("expires_at", "Unknown")
        
        text += f"🔗 {unique_code[:8]}...\n"
        text += f"   📁 {file_name}\n"
        text += f"   👥 {access_count} views\n"
        text += f"   ⏳ {expires_at}\n\n"
    
    if len(links) > 10:
        text += f"...and {len(links) - 10} more links."
    
    await message.reply_text(text)

# Handle link access
@Client.on_message(filters.regex(r'^/start link_'))
async def handle_link_access(client, message: Message):
    """Handle unique link access"""
    unique_code = message.text.split("link_")[1]
    user_id = message.from_user.id
    
    # Check link validity
    is_valid, message_text = await link_system.check_link_validity(unique_code)
    
    if not is_valid:
        await message.reply_text(f"❌ {message_text}")
        return
    
    # Track access
    await link_system.track_link_access(unique_code, user_id)
    
    # Get link info
    link_data = await link_system.get_link_info(unique_code)
    file_id = link_data.get("file_id")
    
    if not file_id:
        await message.reply_text("File not found.")
        return
    
    # Check FSUB first
    from plugins.fsub import fsub_manager
    if fsub_manager:
        can_proceed = await fsub_manager.send_fsub_message(message)
        if not can_proceed:
            return
    
    # Check daily limit for free users
    can_download = await premium_db.track_daily_usage(user_id)
    
    if not can_download:
        from info import DAILY_FREE_LIMIT
        today_downloads = await premium_db.get_today_downloads(user_id)
        
        text = f"❌ **Daily Limit Reached**\n\n"
        text += f"You have downloaded {today_downloads} files today.\n"
        text += f"Free users are limited to {DAILY_FREE_LIMIT} files per day.\n\n"
        text += "**Upgrade to Premium for unlimited downloads!**"
        
        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐ Get Premium", callback_data="premium")],
                [InlineKeyboardButton("🔄 Try Again Tomorrow", callback_data="close")]
            ])
        )
        return
    
    # Send the file
    try:
        await client.send_cached_media(
            chat_id=user_id,
            file_id=file_id,
            caption=f"📁 File shared via unique link\n\n🔗 Link code: `{unique_code}`",
            protect_content=True
        )
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await message.reply_text("Error sending file. Please try again later.")

# Add this to database.py
"""
# Add these methods to your existing database.py
async def update_unique_link(self, unique_code, data):
    col = self.db["unique_links"]
    await col.update_one(
        {"unique_code": unique_code},
        {"$set": data},
        upsert=True
    )

async def get_unique_link(self, unique_code):
    col = self.db["unique_links"]
    return await col.find_one({"unique_code": unique_code})

async def get_user_links(self, user_id):
    col = self.db["unique_links"]
    return await col.find({"created_by": user_id}).to_list(length=None)
"""