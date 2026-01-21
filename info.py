# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01


import re
from os import environ
from Script import script 

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '30121899'))
API_HASH = environ.get('API_HASH', 'd43eb6418b1a9a92fb658130394b0f8d')
BOT_TOKEN = environ.get('BOT_TOKEN', "8407847011:AAFvWe7hjDYwjJwnVXOL1dfB45hqk0fQMTE")

# Pictures for start message
PICS = (environ.get('PICS', 'https://graph.org/file/ce1723991756e48c35aa1.jpg')).split()

# Admins & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '8572902738').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

# Log Channel
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1003636205044'))

# File Channels (4 channels)
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1003569825863 -1003327001243 -1003155580619 -1003544571934').split()]

# Request to join mode (force subscribe)
REQUEST_TO_JOIN_MODE = bool(environ.get('REQUEST_TO_JOIN_MODE', True))
TRY_AGAIN_BTN = bool(environ.get('TRY_AGAIN_BTN', True))

# Auth Channel (first channel as auth)
auth_channel = environ.get('AUTH_CHANNEL', '-1003569825863')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None

# Request Channel
reqst_channel = environ.get('REQST_CHANNEL', '-1003674096367')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None

# Index Request Channel
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))

# Support Group
support_chat_id = environ.get('SUPPORT_CHAT_ID', '')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None

# File Store Channel
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '-1003674096367')).split()]

# Delete Channels
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]

# MongoDB information - FIXED URL
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://hackingyashwant_db_user:RjIucgaU6RsJWPRU@cluster0.euy3vsq.mongodb.net/?retryWrites=true&w=majority&ssl=false")
DATABASE_NAME = environ.get('DATABASE_NAME', "movie_hub_bot")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'movies_collection')

MULTIPLE_DATABASE = bool(environ.get('MULTIPLE_DATABASE', False))

# Other database URIs (if multiple DB is true)
O_DB_URI = environ.get('O_DB_URI', "")
F_DB_URI = environ.get('F_DB_URI', "")
S_DB_URI = environ.get('S_DB_URI', "")

# Premium and Referral Settings
PREMIUM_AND_REFERAL_MODE = bool(environ.get('PREMIUM_AND_REFERAL_MODE', False))
REFERAL_COUNT = int(environ.get('REFERAL_COUNT', '20'))
REFERAL_PREMEIUM_TIME = environ.get('REFERAL_PREMEIUM_TIME', '1month')
PAYMENT_QR = environ.get('PAYMENT_QR', 'https://graph.org/file/ce1723991756e48c35aa1.jpg')
PAYMENT_TEXT = environ.get('PAYMENT_TEXT', '<b>- біАбі†біА…™ ЯбіА Щ ЯбіЗ біШ ЯбіА…іs - \n\n- 30 Аs - 1 бі°біЗбіЗбіЛ\n- 50 Аs - 1 біНбіП…ібіЫ Ьs\n- 120 Аs - 3 біНбіП…ібіЫ Ьs\n- 220 Аs - 6 біНбіП…ібіЫ Ьs\n\nрЯОБ біШ АбіЗбіН…™біЬбіН "УбіЗбіАбіЫбіЬ АбіЗs рЯОБ\n\nвЧЛ …ібіП …ібіЗбіЗбіЕ біЫбіП бі†біЗ А…™"У П\nвЧЛ …ібіП …ібіЗбіЗбіЕ біЫбіП біПбіШбіЗ…і Я…™…ібіЛ\nвЧЛ біЕ…™ АбіЗбіДбіЫ "У…™ ЯбіЗs\nвЧЛ біАбіЕ-"У АбіЗбіЗ біЗxбіШбіЗ А…™біЗ…ібіДбіЗ\nвЧЛ Ь…™…ҐЬ-sбіШбіЗбіЗбіЕ біЕбіПбі°…іЯбіПбіАбіЕ Я…™…ібіЛ\nвЧЛ біНбіЬЯбіЫ…™-біШ ЯбіАПбіЗА sбіЫАбіЗбіАбіН…™…і…Ґ Я…™…ібіЛs\nвЧЛ біЬ…іЯ…™біН…™біЫбіЗбіЕ біНбіПбі†…™біЗs & sбіЗА…™біЗs\nвЧЛ кЬ∞біЬЯ Я біАбіЕбіН…™…і sбіЬбіШбіШбіПАбіЫ\nвЧЛ АбіЗ«ЂбіЬбіЗsбіЫ бі°…™Я Я ЩбіЗ біДбіПбіНбіШЯбіЗбіЫбіЗбіЕ …™…і 1Ь …™кЬ∞ біАбі†біА…™ЯбіАЩ ЯбіЗ\n\nвЬ® біЬбіШ…™ …™біЕ - <code>demo@okxyz</code>\n\nбіДЯ…™біДбіЛ біЫбіП біДЬбіЗбіДбіЛ ПбіПбіЬА біАбіДбіЫ…™бі†біЗ біШЯбіА…і /myplan\n\nрЯТҐ біНбіЬsбіЫ sбіЗ…ібіЕ sбіДАбіЗбіЗ…іsЬбіПбіЫ біА"УбіЫбіЗА біШбіАПбіНбіЗ…ібіЫ\n\nвАЉпЄП біА"УбіЫбіЗА sбіЗ…ібіЕ…™…і…Ґ біА sбіДАбіЗбіЗ…іsЬбіПбіЫ біШЯбіЗбіАsбіЗ …Ґ…™бі†біЗ біЬs sбіПбіНбіЗ біЫ…™біНбіЗ біЫбіП біАбіЕбіЕ ПбіПбіЬ …™…і біЫЬбіЗ біШАбіЗбіН…™біЬбіН</b>')

# Clone Information
CLONE_MODE = bool(environ.get('CLONE_MODE', False))
CLONE_DATABASE_URI = environ.get('CLONE_DATABASE_URI', "")
PUBLIC_FILE_CHANNEL = environ.get('PUBLIC_FILE_CHANNEL', '')

# Links
GRP_LNK = environ.get('GRP_LNK', 'https://t.me/+Jd1FebsBfFBiZjc1')
CHNL_LNK = environ.get('CHNL_LNK', 'https://t.me/+IsEpEZnOKN45NjFl')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'vj_bot_disscussion')
OWNER_LNK = environ.get('OWNER_LNK', 'https://t.me/kingvj01')

# True or False settings
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

# Token Verification
VERIFY = bool(environ.get('VERIFY', False))
VERIFY_SHORTLINK_URL = environ.get('VERIFY_SHORTLINK_URL', '')
VERIFY_SHORTLINK_API = environ.get('VERIFY_SHORTLINK_API', '')
VERIFY_TUTORIAL = environ.get('VERIFY_TUTORIAL', '')
VERIFY_SECOND_SHORTNER = bool(environ.get('VERIFY_SECOND_SHORTNER', False))
VERIFY_SND_SHORTLINK_URL = environ.get('VERIFY_SND_SHORTLINK_URL', '')
VERIFY_SND_SHORTLINK_API = environ.get('VERIFY_SND_SHORTLINK_API', '')

# Shortlink Info
SHORTLINK_MODE = bool(environ.get('SHORTLINK_MODE', False))
SHORTLINK_URL = environ.get('SHORTLINK_URL', '')
SHORTLINK_API = environ.get('SHORTLINK_API', '')
TUTORIAL = environ.get('TUTORIAL', '')

# Others
CACHE_TIME = int(environ.get('CACHE_TIME', 1800))
MAX_B_TN = environ.get("MAX_B_TN", "5")
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'Hello My Dear Friends вЭ§пЄП')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)

# Choose Option Settings 
LANGUAGES = ["malayalam", "mal", "tamil", "tam", "english", "eng", "hindi", "hin", "telugu", "tel", "kannada", "kan"]
SEASONS = ["season 1", "season 2", "season 3", "season 4", "season 5", "season 6", "season 7", "season 8", "season 9", "season 10"]
EPISODES = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40"]
QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]
YEARS = ["1900", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]

# Online Stream and Download
STREAM_MODE = bool(environ.get('STREAM_MODE', True))
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://your-app-name.onrender.com/")

# Rename Info
RENAME_MODE = bool(environ.get('RENAME_MODE', False))

# Auto Approve Info
AUTO_APPROVE_MODE = bool(environ.get('AUTO_APPROVE_MODE', False))

# Start Command Reactions
REACTIONS = ["рЯ§Э", "рЯШЗ", "рЯ§Ч", "рЯШН", "рЯСН", "рЯОЕ", "рЯШР", "рЯ•∞", "рЯ§©", "рЯШ±", "рЯ§£", "рЯШШ", "рЯСП", "рЯШЫ", "рЯШИ", "рЯОЙ", "вЪ°пЄП", "рЯЂ°", "рЯ§У", "рЯШО", "рЯПЖ", "рЯФ•", "рЯ§≠", "рЯМЪ", "рЯЖТ", "рЯСї", "рЯШБ"]

# Database URIs
if MULTIPLE_DATABASE == False:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = DATABASE_URI
    FILE_DB_URI = DATABASE_URI
    SEC_FILE_DB_URI = DATABASE_URI
else:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = O_DB_URI
    FILE_DB_URI = F_DB_URI
    SEC_FILE_DB_URI = S_DB_URI