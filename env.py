import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("CHII_TOKEN")
SERVERS_DB = os.getenv("CHII_SERVERS_DB")
COUNT_DB = os.getenv("CHII_COUNT_DB")
TEMP_DIR = os.getenv("TEMP_DIR")
BOT_OWNER_ID = os.getenv("BOT_OWNER_ID")