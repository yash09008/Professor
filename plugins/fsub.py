import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import FSUB_CHANNELS, FSUB_PROGRESSIVE, FSUB_MSG, FSUB_AFTER_MSG, ADMINS
from database.users_chats_db import db
from utils import temp
import logging

logger = logging.getLogger(__name__)

class FSubManager:
    def __init__(self, bot):
        self.bot = bot
    
    async def check_fsub(self, user_id):
        """Check if user has joined all required channels"""
        not_joined = []
        
        for channel_id in FSUB_CHANNELS[:4]:  # Only check first 4 channels
            try:
                member = await self.bot.get_chat_member(channel_id, user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(channel_id)
            except Exception as e:
                logger.error(f"Error checking channel {channel_id}: {e}")
                not_joined.append(channel_id)
        
        return not_joined
    
    async def get_channel_buttons(self, not_joined_channels):
        """Create buttons for channels user needs to join"""
        buttons = []
        
        for channel_id in not_joined_channels:
            try:
                chat = await self.bot.get_chat(channel_id)
                buttons.append([
                    InlineKeyboardButton(
                        f"Join {chat.title}", 
                        url=chat.invite_link
                    )
                ])
            except Exception as e:
                logger.error(f"Error getting chat {channel_id}: {e}")
        
        # Add Verify button
        if not_joined_channels:
            buttons.append([
                InlineKeyboardButton("✅ I've Joined All", callback_data="fsub_verify")
            ])
        
        return InlineKeyboardMarkup(buttons)
    
    async def send_fsub_message(self, message: Message):
        """Send FSUB message to user"""
        user_id = message.from_user.id
        
        # Check if user is admin
        if user_id in ADMINS:
            return True
        
        # Check FSUB status
        not_joined = await self.check_fsub(user_id)
        
        if not not_joined:
            # User has joined all channels
            return True
        
        # Send FSUB message with progressive count
        joined_count = 4 - len(not_joined)
        remaining_count = len(not_joined)
        
        if FSUB_PROGRESSIVE:
            fsub_text = f"{FSUB_MSG}\n\n📊 Status: {joined_count}/4 channels joined\n⬇️ Remaining: {remaining_count} channels"
        else:
            fsub_text = FSUB_MSG
        
        buttons = await self.get_channel_buttons(not_joined)
        
        # Send message
        sent_msg = await message.reply_text(
            fsub_text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        
        # Store message ID for deletion
        await db.update_user(user_id, {"fsub_msg_id": sent_msg.id})
        
        return False
    
    async def verify_fsub(self, callback_query):
        """Verify FSUB after user clicks button"""
        user_id = callback_query.from_user.id
        
        # Check FSUB status again
        not_joined = await self.check_fsub(user_id)
        
        if not not_joined:
            # User has joined all channels
            await callback_query.message.delete()
            
            # Send welcome message
            await callback_query.message.reply_text(
                FSUB_AFTER_MSG,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📖 ABOUT ME", callback_data="about")],
                    [InlineKeyboardButton("⭐ PREMIUM", callback_data="premium")],
                    [InlineKeyboardButton("🚪 PORTAL", callback_data="portal"),
                     InlineKeyboardButton("🆘 SUPPORT", url="https://t.me/vj_bot_disscussion")],
                    [InlineKeyboardButton("📦 SOURCE CODE", url="https://github.com/VJBots/VJ-Filter-Bot"),
                     InlineKeyboardButton("❌ CLOSE", callback_data="close")]
                ])
            )
            
            await callback_query.answer("✅ Verified! Welcome to the bot.", show_alert=True)
            return True
        else:
            # Still not joined all
            joined_count = 4 - len(not_joined)
            await callback_query.answer(
                f"❌ You still need to join {len(not_joined)} more channels. Currently joined: {joined_count}/4",
                show_alert=True
            )
            return False

# Initialize
fsub_manager = None

def setup_fsub(bot):
    global fsub_manager
    fsub_manager = FSubManager(bot)

# ============================================
# COMMAND HANDLERS
# ============================================

@Client.on_message(filters.command("start") & filters.private)
async def start_with_fsub(client, message: Message):
    """Start command with FSUB check"""
    global fsub_manager
    
    if not fsub_manager:
        setup_fsub(client)
    
    # Check FSUB
    can_proceed = await fsub_manager.send_fsub_message(message)
    
    if can_proceed:
        # User has joined all channels, show main menu
        from Script import script
        await message.reply_text(
            script.START_TXT.format(message.from_user.mention),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 ABOUT ME", callback_data="about")],
                [InlineKeyboardButton("⭐ PREMIUM", callback_data="premium")],
                [InlineKeyboardButton("🚪 PORTAL", callback_data="portal"),
                 InlineKeyboardButton("🆘 SUPPORT", url="https://t.me/vj_bot_disscussion")],
                [InlineKeyboardButton("📦 SOURCE CODE", url="https://github.com/VJBots/VJ-Filter-Bot"),
                 InlineKeyboardButton("❌ CLOSE", callback_data="close")]
            ])
        )

@Client.on_callback_query(filters.regex("^fsub_verify$"))
async def verify_fsub_callback(client, callback_query):
    """Handle FSUB verify callback"""
    global fsub_manager
    
    if not fsub_manager:
        setup_fsub(client)
    
    await fsub_manager.verify_fsub(callback_query)

@Client.on_message(filters.command("fsub") & filters.user(ADMINS))
async def fsub_status(client, message: Message):
    """Check FSUB status (admin only)"""
    user_id = message.from_user.id
    
    if len(message.command) > 1:
        try:
            user_id = int(message.command[1])
        except:
            pass
    
    global fsub_manager
    if not fsub_manager:
        setup_fsub(client)
    
    not_joined = await fsub_manager.check_fsub(user_id)
    joined_count = 4 - len(not_joined)
    
    status_text = f"📊 FSUB Status for user {user_id}:\n"
    status_text += f"✅ Joined: {joined_count}/4 channels\n"
    status_text += f"❌ Remaining: {len(not_joined)} channels\n\n"
    
    if not_joined:
        status_text += "Channels not joined:\n"
        for channel_id in not_joined:
            try:
                chat = await client.get_chat(channel_id)
                status_text += f"• {chat.title} ({channel_id})\n"
            except:
                status_text += f"• {channel_id}\n"
    
    await message.reply_text(status_text)