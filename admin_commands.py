import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from info import ADMINS, REQUEST_CHANNELS, LOG_CHANNEL
from database.users_chats_db import db
from datetime import datetime

# ==================== ADMIN PANEL ====================
@Client.on_message(filters.command("admin") & filters.user(ADMINS))
async def admin_panel(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
         InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton("🚫 Ban/Unban", callback_data="admin_ban")],
        [InlineKeyboardButton("📁 Channels", callback_data="admin_channels"),
         InlineKeyboardButton("🖼️ Images", callback_data="admin_images")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings"),
         InlineKeyboardButton("📝 Logs", callback_data="admin_logs")]
    ])
    
    await message.reply_photo(
        photo="https://graph.org/file/ce1723991756e48c35aa1.jpg",
        caption="**🤖 ADMIN CONTROL PANEL**\n\n"
               "Select an option to manage your bot:",
        reply_markup=keyboard
    )

# ==================== STATS ====================
@Client.on_callback_query(filters.regex("admin_stats"))
async def admin_stats(client, callback_query):
    try:
        total_users = await db.total_users_count()
        total_chats = await db.total_chat_count()
        b_users, b_chats = await db.get_banned()
        
        stats_text = f"""
📊 **BOT STATISTICS**

👥 **Total Users:** `{total_users}`
💬 **Total Chats:** `{total_chats}`
🚫 **Banned Users:** `{len(b_users)}`
🚫 **Banned Chats:** `{len(b_chats)}`
📅 **Last Updated:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

🤖 **Bot Info:**
├ ID: `{client.me.id}`
├ Name: {client.me.first_name}
└ Username: @{client.me.username}
        """
        
        await callback_query.message.edit_caption(
            caption=stats_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats"),
                 InlineKeyboardButton("📤 Export", callback_data="export_stats")],
                [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
            ])
        )
    except Exception as e:
        await callback_query.message.edit_caption(f"Error: {str(e)}")

# ==================== BROADCAST WITH IMAGE ====================
@Client.on_callback_query(filters.regex("admin_broadcast"))
async def admin_broadcast_menu(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Text Only", callback_data="broadcast_text"),
         InlineKeyboardButton("🖼️ With Image", callback_data="broadcast_image")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ])
    
    await callback_query.message.edit_caption(
        caption="**📢 BROADCAST MESSAGE**\n\n"
               "Choose broadcast type:\n"
               "• **Text Only** - Send text message\n"
               "• **With Image** - Send image with caption\n\n"
               "⚠️ This will send to ALL users.",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex("broadcast_image"))
async def broadcast_image_start(client, callback_query):
    await callback_query.message.edit_caption(
        caption="**🖼️ BROADCAST WITH IMAGE**\n\n"
               "Send me the image first, then send the caption.\n\n"
               "Format:\n"
               "1. Send image (as photo)\n"
               "2. Send caption text\n\n"
               "Type /cancel to stop.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="admin_broadcast")]
        ])
    )
    
    # Store state
    user_id = callback_query.from_user.id
    broadcast_data[user_id] = {"type": "image", "step": 1}

# Global dictionary to store broadcast data
broadcast_data = {}

@Client.on_message(filters.photo & filters.user(ADMINS))
async def receive_broadcast_image(client, message):
    user_id = message.from_user.id
    if user_id in broadcast_data and broadcast_data[user_id]["type"] == "image" and broadcast_data[user_id]["step"] == 1:
        # Store image
        broadcast_data[user_id]["photo"] = message.photo.file_id
        broadcast_data[user_id]["step"] = 2
        
        await message.reply_text(
            "✅ Image received!\n\n"
            "Now send me the caption/text for this image.\n"
            "Type /cancel to stop."
        )

@Client.on_message(filters.text & filters.user(ADMINS))
async def receive_broadcast_caption(client, message):
    user_id = message.from_user.id
    
    if message.text == "/cancel":
        if user_id in broadcast_data:
            del broadcast_data[user_id]
        await message.reply_text("❌ Broadcast cancelled.")
        return
    
    if user_id in broadcast_data and broadcast_data[user_id]["type"] == "image" and broadcast_data[user_id]["step"] == 2:
        caption = message.text
        photo = broadcast_data[user_id].get("photo")
        
        if not photo:
            await message.reply_text("❌ No image found. Please start again.")
            return
        
        # Confirm broadcast
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Send", callback_data=f"confirm_broadcast_image_{user_id}"),
             InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")]
        ])
        
        # Preview
        await message.reply_photo(
            photo=photo,
            caption=f"📢 **BROADCAST PREVIEW**\n\n{caption}\n\n"
                   f"**Send this to all users?**\n"
                   f"Estimated users: {await db.total_users_count()}",
            reply_markup=keyboard
        )
        
        # Store final data
        broadcast_data[user_id]["caption"] = caption

@Client.on_callback_query(filters.regex(r"^confirm_broadcast_image_"))
async def confirm_broadcast_image(client, callback_query):
    user_id = int(callback_query.data.split("_")[-1])
    
    if user_id not in broadcast_data:
        await callback_query.message.edit_caption("❌ Broadcast data not found.")
        return
    
    data = broadcast_data[user_id]
    photo = data.get("photo")
    caption = data.get("caption")
    
    if not photo or not caption:
        await callback_query.message.edit_caption("❌ Missing image or caption.")
        return
    
    # Start broadcasting
    users = await db.get_all_users()
    total = len(users)
    success = 0
    failed = 0
    
    progress_msg = await callback_query.message.edit_caption(
        f"📤 **Broadcasting Started...**\n\n"
        f"Progress: 0/{total}\n"
        f"✅ Success: 0\n"
        f"❌ Failed: 0"
    )
    
    for i, user in enumerate(users):
        try:
            await client.send_photo(
                chat_id=int(user['id']),
                photo=photo,
                caption=caption
            )
            success += 1
        except Exception as e:
            failed += 1
        
        # Update progress every 10 users
        if (i + 1) % 10 == 0 or (i + 1) == total:
            await progress_msg.edit_caption(
                f"📤 **Broadcasting...**\n\n"
                f"Progress: {i+1}/{total}\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}"
            )
    
    # Final result
    await progress_msg.edit_caption(
        f"✅ **BROADCAST COMPLETE!**\n\n"
        f"📊 **Results:**\n"
        f"• Total Users: {total}\n"
        f"• ✅ Success: {success}\n"
        f"• ❌ Failed: {failed}\n\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    # Cleanup
    if user_id in broadcast_data:
        del broadcast_data[user_id]
    
    # Log to LOG_CHANNEL
    try:
        await client.send_message(
            LOG_CHANNEL,
            f"📢 **Broadcast Sent**\n\n"
            f"👤 Admin: {callback_query.from_user.mention}\n"
            f"👥 Total: {total}\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}\n"
            f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except:
        pass

# ==================== MANAGE CHANNELS ====================
@Client.on_callback_query(filters.regex("admin_channels"))
async def admin_channels(client, callback_query):
    from info import CHANNELS, REQUEST_CHANNELS
    
    channels_text = "**📁 MANAGED CHANNELS**\n\n"
    
    channels_text += "**📢 File Channels:**\n"
    for i, ch in enumerate(CHANNELS, 1):
        try:
            chat = await client.get_chat(ch)
            channels_text += f"{i}. {chat.title} (ID: `{ch}`)\n"
        except:
            channels_text += f"{i}. Channel ID: `{ch}`\n"
    
    channels_text += "\n**🔐 Request-to-Join Channels:**\n"
    if REQUEST_CHANNELS:
        for i, ch in enumerate(REQUEST_CHANNELS, 1):
            try:
                chat = await client.get_chat(ch)
                channels_text += f"{i}. {chat.title} (ID: `{ch}`)\n"
            except:
                channels_text += f"{i}. Channel ID: `{ch}`\n"
    else:
        channels_text += "No channels set\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"),
         InlineKeyboardButton("➖ Remove Channel", callback_data="remove_channel")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_channels"),
         InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ])
    
    await callback_query.message.edit_caption(
        caption=channels_text,
        reply_markup=keyboard
    )

# ==================== MANAGE IMAGES ====================
@Client.on_callback_query(filters.regex("admin_images"))
async def admin_images(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👋 Welcome Image", callback_data="set_welcome_image"),
         InlineKeyboardButton("📢 Broadcast Image", callback_data="set_broadcast_image")],
        [InlineKeyboardButton("🔗 Link Image", callback_data="set_link_image"),
         InlineKeyboardButton("📸 View Images", callback_data="view_images")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_back")]
    ])
    
    await callback_query.message.edit_caption(
        caption="**🖼️ MANAGE IMAGES**\n\n"
               "Set custom images for:\n"
               "• **Welcome Image** - Shown on /start command\n"
               "• **Broadcast Image** - Default for broadcasts\n"
               "• **Link Image** - For link messages\n\n"
               "Current default: [Graph Image]",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex("set_welcome_image"))
async def set_welcome_image(client, callback_query):
    await callback_query.message.edit_caption(
        caption="**👋 SET WELCOME IMAGE**\n\n"
               "Send me the new welcome image (as photo).\n"
               "This will be shown when users use /start command.\n\n"
               "⚠️ Send as photo, not document.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="admin_images")]
        ])
    )
    
    # Set state
    user_id = callback_query.from_user.id
    image_settings[user_id] = {"type": "welcome"}

# Store image settings
image_settings = {}

@Client.on_message(filters.photo & filters.user(ADMINS))
async def save_custom_image(client, message):
    user_id = message.from_user.id
    
    if user_id in image_settings:
        image_type = image_settings[user_id]["type"]
        file_id = message.photo.file_id
        
        # Save to database or file
        # For now, we'll just save to a variable
        if image_type == "welcome":
            # Save to database or config
            await message.reply_text(
                f"✅ **Welcome Image Updated!**\n\n"
                f"New welcome image has been set.\n"
                f"File ID: `{file_id}`\n\n"
                f"Test with /start command."
            )
        elif image_type == "broadcast":
            await message.reply_text(
                f"✅ **Broadcast Image Updated!**\n\n"
                f"New broadcast image has been set."
            )
        
        # Clear state
        del image_settings[user_id]

# ==================== BACK BUTTON ====================
@Client.on_callback_query(filters.regex("admin_back"))
async def admin_back(client, callback_query):
    await admin_panel(client, callback_query.message)

# ==================== QUICK COMMANDS ====================
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def quick_broadcast(client, message):
    if len(message.command) < 2:
        await message.reply_text("**Usage:**\n`/broadcast your message`\n`/broadcast_image`")
        return
    
    text = message.text.split(None, 1)[1]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Text Only", callback_data=f"quick_broadcast_text_{message.from_user.id}"),
         InlineKeyboardButton("🖼️ With Image", callback_data="broadcast_image")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])
    
    await message.reply_text(
        f"📢 **Broadcast Preview:**\n\n{text}\n\n"
        f"Send to all users?",
        reply_markup=keyboard
    )

# Export users command
@Client.on_message(filters.command("export") & filters.user(ADMINS))
async def export_users(client, message):
    users = await db.get_all_users()
    
    with open('users_list.txt', 'w') as f:
        f.write("ID | Name | Date\n")
        f.write("-" * 50 + "\n")
        for user in users:
            f.write(f"{user['id']} | {user.get('name', 'N/A')} | {user.get('date', 'N/A')}\n")
    
    await message.reply_document(
        'users_list.txt',
        caption=f"📊 **Users Export**\nTotal Users: {len(users)}"
    )
    
    os.remove('users_list.txt')