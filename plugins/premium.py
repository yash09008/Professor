import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import PREMIUM_ENABLED, PREMIUM_PLANS, OWNER_UPI_ID, PAYMENT_QR, ADMINS
from database.premium_db import premium_db
from utils import temp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@Client.on_callback_query(filters.regex("^premium$"))
async def premium_menu(client, callback_query: CallbackQuery):
    """Show premium menu"""
    if not PREMIUM_ENABLED:
        await callback_query.answer("Premium system is disabled", show_alert=True)
        return
    
    user_id = callback_query.from_user.id
    
    # Check if user is already premium
    is_premium = await premium_db.is_premium(user_id)
    
    if is_premium:
        premium_info = await premium_db.get_premium_info(user_id)
        expiry_date = premium_info.get("expiry_date")
        
        text = f"⭐ **PREMIUM STATUS** ⭐\n\n"
        text += f"✅ You are a **Premium User**!\n"
        text += f"📅 Plan: {premium_info.get('plan_name', 'Premium')}\n"
        text += f"⏳ Expires: {expiry_date.strftime('%d %b %Y')}\n"
        text += f"🎁 Payment: {premium_info.get('payment_method', 'Unknown')}\n\n"
        text += "Enjoy unlimited downloads! 🚀"
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )
    else:
        # Show premium plans
        text = "**Want Premium?**\nChoose a method below:\n\n"
        text += "🛡️ **Refer & Earn Premium** (Invite friends, get premium for free)\n"
        text += "💰 **Buy with Referral Points** (Instant using points)\n"
        text += "📊 **Pay with UPI** (Instant activation)\n"
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛡️ Refer & Earn Premium", callback_data="referral_panel")],
                [InlineKeyboardButton("💰 Buy with Points", callback_data="buy_with_points")],
                [InlineKeyboardButton("📊 Pay with UPI", callback_data="premium_plans")],
                [InlineKeyboardButton("🔙 Back", callback_data="start"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^referral_panel$"))
async def referral_panel(client, callback_query: CallbackQuery):
    """Show referral panel"""
    user_id = callback_query.from_user.id
    
    # Get referral stats
    referral_count = await premium_db.get_referral_count(user_id)
    user_points = await premium_db.get_user_points(user_id)
    
    from info import REFERRAL_POINTS_PER_REF, POINTS_TO_DAYS_RATIO
    
    text = "**Referral Panel**\n\n"
    text += f"• Mode: ENABLED ✅\n"
    text += f"• Points per Referral: {REFERRAL_POINTS_PER_REF}\n"
    text += f"• Reward: {POINTS_TO_DAYS_RATIO} pts → 1 days\n"
    text += f"• Your Points: {user_points}\n"
    text += f"• Progress: {referral_count}/∞\n"
    text += f"• Available Redemptions Now: {user_points}\n\n"
    
    # Generate referral link
    bot_username = (await client.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text += f"**Your referral link:**\n`{referral_link}`\n\n"
    text += "Use the buttons below."
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Buy with Points", callback_data="buy_with_points")],
            [InlineKeyboardButton("📋 Copy Referral Link", callback_data=f"copy_{referral_link}")],
            [InlineKeyboardButton("🔙 Back", callback_data="premium"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ]),
        disable_web_page_preview=True
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^buy_with_points$"))
async def buy_with_points(client, callback_query: CallbackQuery):
    """Buy premium with points"""
    user_id = callback_query.from_user.id
    user_points = await premium_db.get_user_points(user_id)
    
    from info import POINTS_TO_DAYS_RATIO
    
    text = f"**Buy Premium with Referral Points**\n\n"
    text += f"• Your points: {user_points}\n"
    text += f"• Reward rate: {POINTS_TO_DAYS_RATIO} pts ⇒ 1 days\n\n"
    text += "Choose a plan below. Points required are calculated from your reward rate.\n"
    
    # Generate referral link
    bot_username = (await client.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    text += f"**Your referral link:**\n`{referral_link}`\n"
    
    buttons = []
    
    # Create point plans
    point_plans = [
        (10, "10 Days"),
        (21, "21 Days"),
        (30, "1 Month"),
        (60, "2 Months"),
        (90, "3 Months"),
        (180, "6 Months"),
        (365, "1 Year")
    ]
    
    for points_needed, plan_name in point_plans:
        if user_points >= points_needed:
            button_text = f"{plan_name} • ({points_needed} pts)"
            callback_data = f"redeem_{points_needed}"
        else:
            button_text = f"{plan_name} • ({points_needed} pts) ❌"
            callback_data = "not_enough"
        
        buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data="referral_panel"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    ])
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^redeem_"))
async def redeem_points(client, callback_query: CallbackQuery):
    """Redeem points for premium"""
    user_id = callback_query.from_user.id
    points_needed = int(callback_query.data.split("_")[1])
    
    success, message = await premium_db.redeem_points(user_id, points_needed)
    
    if success:
        text = f"✅ **Success!**\n\n"
        text += f"You have redeemed {points_needed} points for premium.\n"
        text += f"Enjoy your premium benefits! 🎉"
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Premium", callback_data="premium")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )
    else:
        await callback_query.answer(message, show_alert=True)
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^premium_plans$"))
async def premium_plans(client, callback_query: CallbackQuery):
    """Show premium payment plans"""
    text = "**SHORTNER PLANS**\n**DURATION & PRICE**\n\n"
    
    for days, price in PREMIUM_PLANS.items():
        if days == 1:
            duration = "1 day"
        elif days == 30:
            duration = "1 month"
        elif days == 90:
            duration = "3 months"
        elif days == 180:
            duration = "6 months"
        elif days == 365:
            duration = "1 year"
        else:
            duration = f"{days} days"
        
        text += f"» {duration} : ₹{price}\n"
    
    text += "\n**PAYMENT METHODS**\n"
    text += "• UPI • GPay • PhonePe • PayTM • QR Code\n\n"
    text += "**Premium will be added**\nAUTOMATICALLY ONCE PAID\n\n"
    text += "**After payment:**\n"
    text += "• Send payment screenshot to admin\n"
    text += "• Wait a few minutes for activation ✅"
    
    buttons = []
    
    for days, price in PREMIUM_PLANS.items():
        if days == 1:
            plan_name = "1 Day"
        elif days == 10:
            plan_name = "10 Days"
        elif days == 30:
            plan_name = "1 Month"
        elif days == 90:
            plan_name = "3 Months"
        elif days == 180:
            plan_name = "6 Months"
        elif days == 365:
            plan_name = "1 Year"
        else:
            plan_name = f"{days} Days"
        
        buttons.append([
            InlineKeyboardButton(
                plan_name, 
                callback_data=f"buy_premium_{days}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton("Custom Plan", callback_data="custom_plan"),
        InlineKeyboardButton("QR Code", callback_data="show_qr")
    ])
    
    buttons.append([
        InlineKeyboardButton("🔙 Back", callback_data="premium"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    ])
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^buy_premium_"))
async def buy_premium_plan(client, callback_query: CallbackQuery):
    """Handle premium purchase"""
    user_id = callback_query.from_user.id
    days = int(callback_query.data.split("_")[2])
    price = PREMIUM_PLANS.get(days, 0)
    
    if days == 1:
        plan_name = "1 Day"
    elif days == 30:
        plan_name = "1 Month"
    elif days == 90:
        plan_name = "3 Months"
    else:
        plan_name = f"{days} Days"
    
    text = f"**Purchase Details**\n\n"
    text += f"📅 Plan: {plan_name}\n"
    text += f"💰 Price: ₹{price}\n"
    text += f"👤 User: {callback_query.from_user.mention}\n"
    text += f"🆔 User ID: {user_id}\n\n"
    text += f"**UPI ID:** `{OWNER_UPI_ID}`\n\n"
    text += "**Instructions:**\n"
    text += "1. Send ₹{price} to above UPI ID\n"
    text += "2. Take screenshot of payment\n"
    text += "3. Send screenshot to @kingvj01\n"
    text += "4. Wait for activation (usually within 5 minutes)\n\n"
    text += "**Note:** Keep this chat open for verification."
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Send Screenshot", url=f"https://t.me/kingvj01")],
            [InlineKeyboardButton("🔙 Back", callback_data="premium_plans"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
    )
    
    await callback_query.answer()

@Client.on_callback_query(filters.regex("^show_qr$"))
async def show_qr_code(client, callback_query: CallbackQuery):
    """Show QR code for payment"""
    from info import PAYMENT_QR
    
    text = "**Scan QR Code to Pay**\n\n"
    text += f"**UPI ID:** `{OWNER_UPI_ID}`\n\n"
    text += "After payment, send screenshot to @kingvj01"
    
    await callback_query.message.reply_photo(
        photo=PAYMENT_QR,
        caption=text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="premium_plans")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ])
    )
    
    await callback_query.answer()

# Admin commands
@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_admin(client, message: Message):
    """Add premium to user (admin)"""
    if len(message.command) < 3:
        await message.reply_text("Usage: /addpremium user_id days")
        return
    
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        plan_name = message.command[3] if len(message.command) > 3 else "Admin Added"
    except:
        await message.reply_text("Invalid format. Use: /addpremium user_id days [plan_name]")
        return
    
    await premium_db.add_premium_user(user_id, days, plan_name, "Admin")
    await message.reply_text(f"✅ Premium added for user {user_id} for {days} days.")

@Client.on_message(filters.command("removepremium") & filters.user(ADMINS))
async def remove_premium_admin(client, message: Message):
    """Remove premium from user (admin)"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /removepremium user_id")
        return
    
    try:
        user_id = int(message.command[1])
    except:
        await message.reply_text("Invalid user ID")
        return
    
    await premium_db.remove_premium(user_id)
    await message.reply_text(f"✅ Premium removed for user {user_id}.")

@Client.on_message(filters.command("premiumusers") & filters.user(ADMINS))
async def list_premium_users(client, message: Message):
    """List all premium users (admin)"""
    users = await premium_db.get_all_premium_users()
    
    if not users:
        await message.reply_text("No premium users found.")
        return
    
    text = "**Premium Users List**\n\n"
    for user in users[:50]:  # Limit to 50 users
        user_id = user["user_id"]
        plan = user.get("plan_name", "Unknown")
        expiry = user.get("expiry_date", "Unknown")
        
        if isinstance(expiry, str):
            expiry_date = expiry
        else:
            expiry_date = expiry.strftime("%d %b %Y")
        
        text += f"👤 {user_id} | {plan} | Exp: {expiry_date}\n"
    
    if len(users) > 50:
        text += f"\n...and {len(users) - 50} more users."
    
    await message.reply_text(text)