from pydantic import BaseModel, Field,EmailStr
from datetime import datetime,timezone
from enum import Enum
from typing import Optional


#--------------   User Model -------------------------
class SubscriptionStatus(str,Enum):
    active="active"
    inactive="inactive"
    cancelled="cancelled"
    trail="trail"

class otpModel(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?\d{10,15}$", example="+911234567890")

class LoginModel(BaseModel):
    # email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    otp: str = Field(..., min_length=6, max_length=6, example="123456")
    # password: str

class userModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = Field(default=None, min_length=2, max_length=50, example="john doe") 
    # email: Optional[EmailStr] = Field(..., example="john@example.com")
    phone_number:Optional[str] = Field(pattern=r"^\+?\d{10,15}$", example="+911234567890", default="0")
    # picture: Optional[str] = None
    # social_id_google: Optional[str] = None
    # password: Optional[str] = Field( min_length=8, max_length=128, example="P@ssw0rd123", default=""
    # )
    is_subscribed:bool = Field(default=False)
    subscription_status : str = Field(default=SubscriptionStatus.inactive)
    subcription_type:str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at:Optional[datetime] = None
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                # "email": "john@example.com",
                "phone_number": "+911234567890",
                # "picture": "None",
                # "social_id_google": "",
                # "password": "P@ssw0rd123",
                "is_subscribed": True,
                "subscription_status": "active",
                "subcription_type":""
                
            }
        }
    

# ----------------------- session Table -------------------------

class sessionTable(BaseModel):
    userId:str = Field(default="")
    Meta_description:Optional[str] = Field(...,min_length=2, max_length=50, example="this is about chat")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at:Optional[datetime] = None 
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "64f2a9c2f4a4b8a2f8d3d12a",
                "meta_description": "This is about chat",
                "created_at": "2025-07-17T12:34:56Z",
                "updated_at": None
            }
        }
        
        
# --------------------- chat Table ------------------------------

# class chat_Table(BaseModel):
#     sessionId:str = Field(default=None, alias="_id")
#     content: str
#     is_bookmark:bool = Field(default=False)
#     created_at:datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     updated_at:Optional[datetime] = None  
    
#     class Config:
#         validate_by_name = True
#         json_schema_extra = {
#             "example": {
#                 "sessionId": "64f2a9c2f4a4b8a2f8d3d12a",
#                 "content": "This is about chat",
#                 "is_bookmark":"true",
#                 "created_at": "2025-07-17T12:34:56Z",
#                 "updated_at": None
#             }
#         }
        
        
# -------------------------- Payment History --------------------------
class PaymentType(str,Enum):
    credit_card = "credit_card"
    debit_card = "debit_card"
    upi = "upi"
    net_banking = "net_banking"
    wallet = "wallet"
    
class PaymentStatus(str, Enum): 
    success = "success"
    failed = "failed"
    pending = "pending"
    
    
class payment_History(BaseModel):
    userId:str = Field(default=None)
    amount:float = Field(..., gt=0, example=499.99)
    Plan:str = Field(..., min_length=2, example="Premium Plan")
    start_Date:datetime = Field(default_factory=datetime.now(timezone.utc))
    time_period: str = Field(..., example="1 month")
    status: PaymentStatus = Field(default=PaymentStatus.pending)
    payment_type: PaymentType = Field(..., example="upi")
    transaction_id: Optional[str] = Field(None, example="TXN123456789")
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "64f2a9c2f4a4b8a2f8d3d12a",
                "amount": 499.99,
                "plan": "Premium Plan",
                "start_date": "2025-07-17T12:34:56Z",
                "time_period": "1 month",
                "status": "success",
                "payment_type": "upi",
                "transaction_id": "TXN123456789"
            }
        }



# --------------------------------  Bookmark Tabels ---------------------------------------------

class bookmark_history(BaseModel):
    userId:str = Field(default=None)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at:Optional[datetime] = None
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "userId":"64f2a9c2f4a4b8a2f8d3d12a",
                "content":"this is my first Bookmark",
                 "created_at": "2025-07-17T12:34:56Z",
                "updated_at": None        
            }
        }
    
    