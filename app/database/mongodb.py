from pymongo import MongoClient
from pymongo.database import Database
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from dotenv import load_dotenv
import os
load_dotenv()

# collection name for chathostory

tablehistory_collectionname = os.getenv("COLLECTION_NAME")
class MongoDb:
    client: MongoClient = None


def get_mongodbconnect() -> Database:
    try:
        mongo_url = os.getenv("MONGODB_URL")
        db_name = os.getenv("DB_NAME")
        if MongoDb.client is None:
            if not mongo_url or not db_name:
                raise ValueError("MONGODB_URL and DB_NAME must be set in environment variables")
            
            MongoDb.client = MongoClient(mongo_url)

        return MongoDb.client[db_name]
    
    except Exception as e:
        raise RuntimeError(f"MongoDB connection error: {e}")
    



# get memory from the mongodb history

mongo_url = os.getenv("MONGODB_URL")
db_name = os.getenv("DB_NAME")
def get_memory(sessionid:str) -> BaseChatMessageHistory:
    chat_history = MongoDBChatMessageHistory(
        connection_string=mongo_url,
        session_id=sessionid,
        database_name=db_name,
        collection_name=tablehistory_collectionname
    )
    # memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True)
    print("this is the session id", chat_history)
    return chat_history



# -------------------  get the data from mongodb -----------------------------
def get_data_from_mongodb(collection_name: str):
    db = get_mongodbconnect()
    return db[collection_name]