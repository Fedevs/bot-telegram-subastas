from dotenv import load_dotenv
import os

load_dotenv() 

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
APPWRITE_ENDPOINT = os.getenv('APPWRITE_ENDPOINT')
APPWRITE_PROJECT_ID = os.getenv('APPWRITE_PROJECT_ID')
APPWRITE_API_KEY = os.getenv('APPWRITE_API_KEY')
APPWRITE_TELEGRAM_BOT_DATABASE_ID = os.getenv('APPWRITE_TELEGRAM_BOT_DATABASE_ID')
APPWRITE_SUBASTAS_COLLECTION_ID = os.getenv('APPWRITE_SUBASTAS_COLLECTION_ID')
