from pymongo import MongoClient
from pymongo.database import Database
from langchain_community.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from dotenv import load_dotenv
from langchain.schema import BaseMessage
from datetime import datetime

from langchain_core.messages import message_to_dict



import os, json
load_dotenv()

import logging

logger = logging.getLogger(__name__)


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
    



# class MongoDBChatMessageHistoryWithTimestamp(MongoDBChatMessageHistory):
#     def add_message(self, message: BaseMessage) -> None:
#         """Append the message to the record in MongoDB with created_at timestamp."""
#         from pymongo import errors

#         try:
#             message_type = message.type
#             if message_type == "human":
#                 message.content = remove_censored_words(message.content)
            
#             self.collection.insert_one(
#                 {
#                     "SessionId": self.session_id,
#                     "History": json.dumps(message_to_dict(message)),
#                     "created_at": datetime.now(),  # Stored as MongoDB Date type
#                 }
#             )
#         except errors.WriteError as err:
#             logger.error(err)


class MongoDBChatMessageHistoryWithTimestamp(MongoDBChatMessageHistory):
    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in MongoDB with created_at timestamp."""
        from pymongo import errors
        # removing sensorted words
        from app.utils.helper import remove_censored_words
        from copy import deepcopy
        try:
            # Store sanitized copy for human messages
            message_dict = message_to_dict(message)
            if message.type == "human":
                sanitized_message_dict = deepcopy(message_dict)
                sanitized_message_dict["data"]["content"] = remove_censored_words(
                    message_dict["data"]["content"]
                )
            else:
                # Keep AI messages as they are
                sanitized_message_dict = message_dict

        
            self.collection.insert_one(
                {
                    "SessionId": self.session_id,
                    "History": json.dumps(sanitized_message_dict),
                    # Stored as MongoDB Date type
                    "created_at": datetime.now(),  
                }
            )

        except errors.WriteError as err:
            logger.error(err)

# get memory from the mongodb history

mongo_url = os.getenv("MONGODB_URL")
db_name = os.getenv("DB_NAME")
def get_memory(sessionid:str) -> BaseChatMessageHistory:
    
    chat_history = MongoDBChatMessageHistoryWithTimestamp(
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