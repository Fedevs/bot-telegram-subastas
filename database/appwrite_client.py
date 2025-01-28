from datetime import datetime
from appwrite.client import Client
from appwrite.id import ID
from appwrite.query import Query
from appwrite.services.databases import Databases
from config import APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID, APPWRITE_API_KEY, APPWRITE_TELEGRAM_BOT_DATABASE_ID, APPWRITE_SUBASTAS_COLLECTION_ID

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

databases = Databases(client)

def create_auction(auction_data):
    try:
        result = databases.create_document(
            database_id=APPWRITE_TELEGRAM_BOT_DATABASE_ID,
            collection_id=APPWRITE_SUBASTAS_COLLECTION_ID,
            document_id=ID.unique(),
            data=auction_data
        )
        return result
    except Exception as e:
        print(f"Error creating auction: {str(e)}")
        raise

def get_active_auctions():
    try:
        result = databases.list_documents(
            database_id=APPWRITE_TELEGRAM_BOT_DATABASE_ID,
            collection_id=APPWRITE_SUBASTAS_COLLECTION_ID,
            queries=[
                Query.greater_than('end_date', datetime.now().strftime("%m/%d/%Y %H:%M")),
                Query.order_asc('end_date')
            ]
        )
        return result['documents']
    except Exception as e:
        print(f"Error fetching auctions: {str(e)}")
        return []

def get_auction_by_id(auction_id):
    try:
        result = databases.get_document(
            database_id=APPWRITE_TELEGRAM_BOT_DATABASE_ID,
            collection_id=APPWRITE_SUBASTAS_COLLECTION_ID,
            document_id=auction_id
        )
        return result
    except Exception as e:
        print(f"Error fetching auction: {str(e)}")
        return None

def update_auction(auction_id, auction_data):
    try:
        result = databases.update_document(
            database_id=APPWRITE_TELEGRAM_BOT_DATABASE_ID,
            collection_id=APPWRITE_SUBASTAS_COLLECTION_ID,
            document_id=auction_id,
            data=auction_data
        )
        return result
    except Exception as e:
        print(f"Error updating auction: {str(e)}")
        raise

def place_bid(auction_id, user_id, amount):
    # Implementar la lógica para registrar una oferta en Appwrite
    pass

# Agregar más funciones según sea necesario