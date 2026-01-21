# ============================================
# ADVANCED 4-CHANNEL FSUB + PREMIUM BOT CONFIG
# ============================================

import re
import os
from os import environ
from Script import script 

id_pattern = re.compile(r'^.\d+$')

# ============================================
# BOT CREDENTIALS (Aapke original)
# ============================================
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '30121899'))
API_HASH = environ.get('API_HASH', 'd43eb6418b1a9a92fb658130394b0f8d')
BOT_TOKEN = environ.get('BOT_TOKEN', "8407847011:AAFvWe7hjDYwjJwnVXOL1dfB45hqk0fQMTE")

# ============================================
# 4-CHANNEL FSUB SYSTEM
# ============================================
FSUB_CHANNELS = [
    int(ch) if id_pattern.search(ch) else ch 
    for ch in environ.get('FSUB_CHANNELS', '-1003569825863 -1003327001243 -1003155580619 -1003544571934').split()
]

# Progressive FSUB - Agar 1 join hai toh 3 dikhayega
FSUB_PROGRESSIVE = bool(environ.get('FSUB_PROGRESSIVE', True))

# FSUB Messages
FSUB_MSG = environ.get('FSUB_MSG', 'Hello Professor 🎉\n\nYou need to join all my channels to use me\n\nKindly Please join channels...')
FSUB_AFTER_MSG = environ.get('FSUB_AFTER_MSG', 'Hello Professor 😊\n\nI can store private files in Specified Channel and other users can access it from special link.')

# ============================================
# PREMIUM & DAILY LIMIT SYSTEM
# ============================================
PREMIUM_ENABLED = bool(environ.get('PREMIUM_ENABLED', True))
DAILY_FREE_LIMIT = int(environ.get('DAILY_FREE_LIMIT', 5))
FREE_USER_MAX_DOWNLOADS = 5  # Free users can download only 5 files/day

# Premium plans (Days: Price in ₹)
PREMIUM_PLANS = {
    1: 30,     # 1 day
    10: 60,    # 10 days
    30: 99,    # 1 month
    90: 249,   # 3 months
    180: 499,  # 6 months
    365: 799   # 1 year
}

# ============================================
# REFERRAL SYSTEM
# ============================================
REFERRAL_ENABLED = bool(environ.get('REFERRAL_ENABLED', True))
REFERRAL_POINTS_PER_REF = int(environ.get('REFERRAL_POINTS_PER_REF', 1))
POINTS_TO_DAYS_RATIO = int(environ.get('POINTS_TO_DAYS_RATIO', 1))  # 1 point = 1 day premium

# ============================================
# UNIQUE LINK GENERATION SYSTEM
# ============================================
UNIQUE_LINK_ENABLED = bool(environ.get('UNIQUE_LINK_ENABLED', True))
LINK_PREFIX = environ.get('LINK_PREFIX', 'https://t.me/')
LINK_LENGTH = int(environ.get('LINK_LENGTH', 10))
LINK_EXPIRY_DAYS = int(environ.get('LINK_EXPIRY_DAYS', 7))

# ============================================
# ADMIN & USERS
# ============================================
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '8572902738').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

# ============================================
# CHANNELS & GROUPS
# ============================================
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003636205044'))
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1003569825863 -1003327001243 -1003155580619 -1003544571934').split()]

# File Channels
FILE_CHANNEL = int(environ.get('FILE_CHANNEL', '-1003569825863'))

# Request Channel
REQUEST_TO_JOIN_MODE = bool(environ.get('REQUEST_TO_JOIN_MODE', True))
TRY_AGAIN_BTN = bool(environ.get('TRY_AGAIN_BTN', True))
auth_channel = environ.get('AUTH_CHANNEL', '-1003569825863')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None

# Support
SUPPORT_CHAT_ID = environ.get('SUPPORT_CHAT_ID', '')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'vj_bot_disscussion')

# ============================================
# MONGODB DATABASE
# ============================================
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://hackingyashwant_db_user:RjIucgaU6RsJWPRU@cluster0.euy3vsq.mongodb.net/?retryWrites=true&w=majority&ssl=false")
DATABASE_NAME = environ.get('DATABASE_NAME', "movie_hub_bot")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'movies_collection')

# Premium users collection
PREMIUM_COLLECTION = environ.get('PREMIUM_COLLECTION', 'premium_users')
USAGE_COLLECTION = environ.get('USAGE_COLLECTION', 'daily_usage')

# ============================================
# PAYMENT SETTINGS
# ============================================
PAYMENT_QR = environ.get('PAYMENT_QR', 'https://graph.org/file/ce1723991756e48c35aa1.jpg')
OWNER_UPI_ID = environ.get('OWNER_UPI_ID', 'demo@okxyz')
PAYMENT_METHODS = ['UPI', 'GPay', 'PhonePe', 'PayTM', 'QR Code']

# ============================================
# BOT SETTINGS
# ============================================
PICS = (environ.get('PICS', 'https://graph.org/file/ce1723991756e48c35aa1.jpg')).split()

# True/False settings
AI_SPELL_CHECK = bool(environ.get('AI_SPELL_CHECK', True))
PM_SEARCH = bool(environ.get('PM_SEARCH', True))
BUTTON_MODE = bool(environ.get('BUTTON_MODE', True))
MAX_BTN = bool(environ.get('MAX_BTN', True))
IS_TUTORIAL = bool(environ.get('IS_TUTORIAL', False))
IMDB = bool(environ.get('IMDB', False))
AUTO_FFILTER = bool(environ.get('AUTO_FFILTER', True))
AUTO_DELETE = bool(environ.get('AUTO_DELETE', True))
LONG_IMDB_DESCRIPTION = bool(environ.get("LONG_IMDB_DESCRIPTION", False))
SPELL_CHECK_REPLY = bool(environ.get("SPELL_CHECK_REPLY", True))
MELCOW_NEW_USERS = bool(environ.get('MELCOW_NEW_USERS', True))
PROTECT_CONTENT = bool(environ.get('PROTECT_CONTENT', False))
PUBLIC_FILE_STORE = bool(environ.get('PUBLIC_FILE_STORE', True))
NO_RESULTS_MSG = bool(environ.get("NO_RESULTS_MSG", False))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))

# ============================================
# LINKS
# ============================================
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/+Jd1FebsBfFBiZjc1')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/+IsEpEZnOKN45NjFl')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'vj_bot_disscussion')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/kingvj01')

# ============================================
# OTHER SETTINGS
# ============================================
CACHE_TIME = int(environ.get('CACHE_TIME', 1800))
MAX_B_TN = environ.get("MAX_B_TN", "5")
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'Hello My Dear Friends вЭ§пЄП')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)

# ============================================
# STREAM MODE
# ============================================
STREAM_MODE = bool(environ.get('STREAM_MODE', True))
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://your-app-name.onrender.com/")

# ============================================
# REACTIONS
# ============================================
REACTIONS = ["рЯ§Э", "рЯШЗ", "рЯ§Ч", "рЯШН", "рЯСН", "рЯОЕ", "рЯШР", "рЯ•∞", "рЯ§©", "рЯШ±", "рЯ§£", "рЯШШ", "рЯСП", "рЯШЫ", "рЯШИ", "рЯОЙ", "вЪ°пЄП", "рЯЂ°", "рЯ§У", "рЯШО", "рЯПЖ", "рЯФ•", "рЯ§≠", "рЯМЪ", "рЯЖТ", "рЯСї", "рЯШБ"]

# ============================================
# VALIDATION
# ============================================
def validate_channels():
    """Validate that we have exactly 4 channels"""
    if len(FSUB_CHANNELS) < 4:
        print(f"⚠️ WARNING: Only {len(FSUB_CHANNELS)} FSUB channels configured. Need 4 channels.")
    elif len(FSUB_CHANNELS) > 4:
        print(f"⚠️ WARNING: {len(FSUB_CHANNELS)} FSUB channels configured. Using first 4.")
        global FSUB_CHANNELS
        FSUB_CHANNELS = FSUB_CHANNELS[:4]
    
    print(f"✅ FSUB System: {len(FSUB_CHANNELS)} channels configured")

# Run validation
validate_channels()

print(f"""
🤖 BOT CONFIGURATION LOADED
===========================
📊 FSUB Channels: {len(FSUB_CHANNELS)}/4
⭐ Premium System: {'ENABLED' if PREMIUM_ENABLED else 'DISABLED'}
🎯 Daily Free Limit: {DAILY_FREE_LIMIT} files
🔗 Unique Links: {'ENABLED' if UNIQUE_LINK_ENABLED else 'DISABLED'}
👑 Admins: {len(ADMINS)}
📁 File Channel: {FILE_CHANNEL}
""")