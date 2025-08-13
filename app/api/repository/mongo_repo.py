from app.models.foundational_model import userModel, LoginModel,sessionTable
from app.api.repository.mongo_services import MongoService
from fastapi import HTTPException, Response, Request
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from app.utils.sms_services import CustomSmsService
# from app.utils.sms_services import sms_services
from enum import Enum
import bcrypt
import json
import jwt
import os
from bson import ObjectId



  
chathistory =  os.getenv("COLLECTION_NAME")
userdetails = os.getenv("USERDETAILS_COLLECTION")
sessionDetail = os.getenv("SESSION_DETAILS")
bookmarkDetail = os.getenv("BOOKMARK_DETAILS")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60


if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not set in environment variables.")

class ChatRepository:
    def __init__(self):
        self.service = MongoService(collection_name=chathistory)
        
    def get_user_chat_history(self,SessionId: str,page: int = 1, limit: int = 20):
        
            skip = (page -1 ) * limit
            
            pipeline = [
                {"$match":{"SessionId":SessionId}},
                # { "$sort": { "created_at": -1 } }, 
                { "$skip": skip },
                { "$limit": limit },
                {
                     "$project": {
                    "_id": {"$toString": "$_id"},
                    "SessionId": 1,
                    "History": 1,
                    "userId": 1
                    }
                }
            ]      
            results = list(self.service.custom_aggregate(pipeline))  
            for doc in results:
                history = doc.get("History")
                if isinstance(history,str):
                    try:
                        doc["History"] = json.loads(history)
                    except json.JSONDecodeError:
                        pass

            if not results:
                raise HTTPException(status_code=404, detail="No chat History found for this user.")
            
            total_count = self.service.custom_count_documents({ "SessionId": SessionId })

            return {
                "success": True,
                "total": total_count,
                "page": page,
                "limit": limit,
                "data": results
            }
    
    def insertone_custom_data(self,data:object):
        self.service.custom_insert_one(data)
        return True   
        

    def count_documents(self,query:dict):
        count = self.service.custom_count_documents(query)
        return count




class Userdetails():
    def __init__(self):
        self.service = MongoService(collection_name=userdetails)
    
    @staticmethod
    def __create_access_token(data: dict, expires_delta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def __convert_enum_values(self, data: dict) -> dict:
        for key, value in data.items():  
            if isinstance(value, Enum):
                data[key] = value.value
        return data
    
    def __hash_password(self, plain_password:str) -> str:
        salt = bcrypt.gensalt()
        hashedpassword = bcrypt.hashpw(plain_password.encode('utf-8'), salt=salt)
        return hashedpassword.decode('utf-8')
    
    @staticmethod
    def __clean_mongo_doc(doc: dict) -> dict:
        if "_id" in doc and isinstance(doc["_id"], dict) and "$oid" in doc["_id"]:
            doc["_id"] = str(doc["_id"]["$oid"])
        return doc
    
    
    def registernewuser(self, data:userModel):
        user_data_dict = data.model_dump(exclude_none=True)
        user_data_dict = self.__convert_enum_values(user_data_dict)
         
        
        # query = {
        #     "$or": []
        # }
        # print("user_data_dict", user_data_dict)
        # if user_data_dict.get("email"):
        #     query["$or"].append({"email": user_data_dict["email"]})
            
        # if user_data_dict.get("phone_number"):
        #     query["$or"].append({"phone_number": user_data_dict["phone_number"]})
        
        # if not query["$or"]:
        #     raise HTTPException(status_code=400, detail="phone number must be provided for registration.")
        
        # existing_user = self.service.custom_find_one(query)
        
        # print("user existing_user", existing_user)
        
        # if existing_user:
        #     if existing_user.get("email") == user_data_dict.get("email"):
        #         raise HTTPException(status_code=409, detail="User with this email already registered.")
            
        #     elif existing_user.get("phone_number") == user_data_dict.get("phone_number"):
        #         raise HTTPException(status_code=409, detail="User with this phone number already registered.")
            
        #     else:
        #         raise HTTPException(status_code=409, detail="User already registered.")
        
        # if "password" in user_data_dict:
        #     user_data_dict["password"] = self.__hash_password(user_data_dict['password'])
    
        try:
            insert_result = self.service.custom_insert_one(user_data_dict)
            return insert_result.inserted_id
        except HTTPException as e:
            raise e
        
    
    def googleauthentication(self, request:Request, userinfo:object):
        try:
            google_social_id = userinfo['sub'] 
            email = userinfo.get('email')
            name = userinfo.get('name')
            picture = userinfo.get('picture')
            
            existing_user_db = self.service.custom_find_one({"social_id_google": google_social_id})
            
            if existing_user_db:
                existing_user_db = self.__clean_mongo_doc(existing_user_db)
                user_in_db = userModel(**existing_user_db)
                print(f"User {user_in_db.email} logged in via Google (existing social ID)")
                access_token = self.__create_access_token(
                        {"sub": user_in_db.email, "user_id": str(user_in_db.id), "provider": "google"}
                    )
                res = {
                    "message": "Login successful",
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": user_in_db.model_dump(by_alias=True, exclude_none=True) 
                }
                return res
            
            if email:
                existing_user_by_email_db = self.service.custom_find_one({"email": email})
                if existing_user_by_email_db:
                    update_result = self.service.custom_update_one(
                        {"_id": existing_user_by_email_db["_id"]},
                        {"$set": {"social_id_google": google_social_id, "picture": picture}}
                        )
                    existing_user_by_email_db = self.__clean_mongo_doc(existing_user_by_email_db)
                    user_in_db = userModel(**existing_user_by_email_db)
                    user_in_db.social_id_google = google_social_id 
                    user_in_db.picture = picture
                    
                    print(f"User {email} account linked to Google ID.")
                    access_token = self.__create_access_token(
                        {"sub": user_in_db.email, "user_id": str(user_in_db.id), "provider": "google"}
                    )
                    res = {
                        "message": "Login successful",
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": user_in_db.model_dump(by_alias=True, exclude_none=True) 
                    }
                    return res
                
            new_user_data = {
                "email": email,
                "name": name,
                "picture": picture,
                "social_id_google": google_social_id,
                # "social_id_facebook": None 
            }
            
            new_user_data = userModel(**new_user_data)
            insert_result = self.service.custom_insert_one(new_user_data)
            created_user_id = insert_result.inserted_id
            created_user_db = self.service.custom_find_one({"_id": created_user_id})
            created_user_db = self.__clean_mongo_doc(created_user_db)
            user_in_db = userModel(**created_user_db)
            print(f"User {user_in_db.email} logged in via Google (existing social ID)")
            access_token = self.__create_access_token(
                    {"sub": user_in_db.email, "user_id": str(user_in_db.id), "provider": "google"}
                )
            res = {
                "message": "Registration successful",
                "access_token": access_token,
                "token_type": "bearer",
                "user": user_in_db.model_dump(by_alias=True, exclude_none=True) 
            }
            return res

        except HTTPException as e:
            raise e
    
    
    def send_user_otp(self, phone: str):
      
        if not phone:
            raise HTTPException(status_code=400, detail="Phone number is required.")
        
        phone = phone.strip()
        if not phone.startswith("+"):
            raise HTTPException(status_code=400, detail="Phone number must start with '+' followed by country code.")
        
        if not phone[1:].isdigit() or len(phone) < 10 or len(phone) > 15:
            raise HTTPException(status_code=400, detail="Invalid phone number format.")
        
        sms_service = CustomSmsService(phone=phone)
        sms_service.notify_user()
        return {"message": "OTP sent successfully."}
    
        
    def verify_and_login_user(self, data: LoginModel, response: Response):
        login_data = data.model_dump(exclude_none=True)
        # login_data = data.dict(exclude_none=True)
        phone = login_data.get("phone_number")
        if not phone:
            raise HTTPException(status_code=400, detail="Phone number is required.")
        
        phone = phone.strip()
        if not phone.startswith("+"):
            raise HTTPException(status_code=400, detail="Phone number must start with '+' followed by country code.")
        
        if not phone[1:].isdigit() or len(phone) < 10 or len(phone) > 15:
            raise HTTPException(status_code=400, detail="Invalid phone number format.")
        query = {}
        # if login_data.get("email"):
        #     query["email"] = login_data["email"]
        
        query["phone_number"] = phone
        
        
        print("--------------------", login_data)
        # verify the otp
        verification_result = CustomSmsService.verify_otp(phone=phone, user_input=login_data.get("otp"))
        if not verification_result:
            raise HTTPException(status_code=401, detail="Invalid OTP or OTP expired.")
        
        user = self.service.custom_find_one(query)      
        user = self.__clean_mongo_doc(user) if user else None
        if not user:
            registered_user = self.registernewuser(userModel(**{"phone_number": phone}))
            
            if not registered_user:
                raise HTTPException(status_code=500, detail="Failed to register user.")
            
            access_token = self.__create_access_token(
                {"phone": query["phone_number"], "user_id": registered_user}
            )
            
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            return {"message": "Login successful", "user_id": str(registered_user)}  
            
            # raise HTTPException(status_code=401, detail="Invalid credentials.")
        
        # if not bcrypt.checkpw(login_data["password"].encode("utf-8"), user["password"].encode("utf-8")):
        #     raise HTTPException(status_code=401, detail="Invalid credentials.")
        
        access_token = self.__create_access_token(
                    {"phone": user["phone_number"], "user_id": str(user["_id"])}
                )
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        
        return {"message": "Login successful", "user_id": str(user["_id"])}
        
        
        
# ------------- --------- class to Handle all session Logic ----------------------------------    
class HandleSessionLogic:
    
    def __init__(self):
        self.service = MongoService(collection_name=sessionDetail)
    
    def create_new_session_chat(self,userId:str):
        try:     
            if not userId:
                raise HTTPException(status_code=400, detail="User Id not found")
            
            session = sessionTable(userId=userId,Meta_description="New Chat")
            session_data = session.model_dump(by_alias=True)
                            
            result = self.service.custom_insert_one(session_data)         
            return result.inserted_id
        
        except HTTPException as e:
            raise e

    
    def updated_session_chat_name(self, sessionId: str, new_name: str):

        try:
            if not sessionId:
                raise HTTPException(status_code=400, detail="Session ID not found")
            
            self.service.custom_findOneAndUpdate(
                {"_id": ObjectId(sessionId)},
                {"$set": {"Meta_description": new_name[:30]}}
            )
                    
        except HTTPException as e:
            raise e


class GetchatApis:
    
    def __init__(self):
        self.sessionTable = MongoService(collection_name=sessionDetail)
        self.chatTable = MongoService(collection_name=chathistory)
        
    # function to get chat metaData and session ID
    def get_chat_session(self,userId:str, page: int = 1, limit: int = 15):
        try:
            if not userId:
                raise HTTPException(status_code=400, detail="User Id not found")
            
            skip = (page -1 ) * limit
            
            pipeline = [
                    { "$match": { "userId": userId } },
                    # { "$sort": { "created_at": -1 } }, 
                    { "$skip": skip },
                    { "$limit": limit },
                {
                    "$project": {
                        "_id": { "$toString": "$_id" },
                        "userId": 1,
                        "Meta_description": 1,
                        "created_at": 1,
                        "updated_at": 1
                    }
                }
            ]

            response = list(self.sessionTable.custom_aggregate(pipeline))
            if not response:
                raise HTTPException(status_code=404, detail="No chat sessions found for this user.")
                                   
            total_count = self.sessionTable.custom_count_documents({ "userId": userId })
            
            return {
                "success": True,
                "total": total_count,
                "page": page,
                "limit": limit,
                "data": response
            }
            
            
            
          
            
        except HTTPException as e:
            raise e
    

# -------------------------------- class for Bookmark logic Handling ------------------------------------------------
    
class BookmarkApis:
    def __init__(self):
        self.bookMarkTabel = MongoService(collection_name=bookmarkDetail)
        
    
    def create_bookmark_list(self,data):
        try:
            bookmark_data = data.model_dump(exclude_none=True)
            result = self.bookMarkTabel.custom_insert_one(bookmark_data)
            
            return {"success": True, "inserted_id": result.inserted_id if result else None}
        
        except HTTPException as e:
            raise e
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create bookmark: {str(e)}")
    
    
    def get_bookmark_data(self,userId:str,page: int = 1, limit: int = 10):
        try:
            if not userId:
                raise HTTPException(status_code=400, detail="User Id is not Found")

            skip = (page - 1) * limit
            
            pipeline = [
                    { "$match": { "userId": userId } },
                    # { "$sort": { "created_at": -1 } }, 
                    { "$skip": skip },
                    { "$limit": limit },
                {
                    "$project": {
                        "_id": { "$toString": "$_id" },
                        "userId": 1,
                        "content": 1,
                        "created_at": 1,
                        "updated_at": 1
                    }
                }
            ]
            
            response = list(self.bookMarkTabel.custom_aggregate(pipeline))
            
            if not response:
                raise HTTPException(status_code=404, detail="No Bookmark for this user.")
            
            
            total_count = self.bookMarkTabel.custom_count_documents({ "userId": userId })

            return {
                "success": True,
                "total": total_count,
                "page": page,
                "limit": limit,
                "data": response
            }
        
        
        except HTTPException as e:
            raise e
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get bookmark: {str(e)}")
        
        
        
    def delete_bookmark_by_id(self, bookmarkId: str):
        try:
            if not bookmarkId:
                raise HTTPException(status_code=400, detail="Bookmark ID is not provided.")
            
            result = self.bookMarkTabel.custom_delete_one({"_id": ObjectId(bookmarkId)})
        
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Bookmark not found.")
        
            return result
        
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete bookmark: {str(e)}")
        
    
    



chathistoryrepo = ChatRepository()
# userauth = Userdetails()