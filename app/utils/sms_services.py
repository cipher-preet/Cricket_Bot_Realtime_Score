from app.api.repository.mongo_services import MongoService
from datetime import datetime, timedelta, timezone
from twilio.rest import Client
import random
import os



# Find the environment variables for Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID") 
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OTP_COLLECTION = os.getenv("OTP_COLLECTION")
# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

class SmsServices:
    
    @staticmethod
    def _send_sms(to: str, body: str) -> bool:
        try:
            message = client.messages.create(
                body=body,
                from_=TWILIO_PHONE_NUMBER,
                to=to
            )
            return True if message.sid else False
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False


class CustomSmsService(SmsServices):
    
    def __init__(self, phone: str):
        self.service = MongoService(collection_name=OTP_COLLECTION)
        self.verification_code = self._generate_verification_code()
        self.phone = phone
        self.expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        
    def _generate_verification_code(self) -> str:
        """Generate a random 6-digit verification code."""
        return str(random.randint(100000, 999999))
    
    def notify_user(self):
        message = f"Your OTP for verifying your Stumpzy account is {self.verification_code}. Do not share this code with anyone."
        success = self._send_sms(self.phone, message)

        if success:
            print("SMS sent successfully!")
            self.service.custom_update_one(
                {"phone": self.phone},
                { 
                    "otp": self.verification_code,
                    "expires_at": self.expiry,
                    "created_at": datetime.now(timezone.utc),
                    "attempts": 0   
                },
                upsert=True
            )
        else:
            print("SMS sending failed.")

    @classmethod
    def verify_otp(cls, phone: str, user_input: str) -> bool:
        service = MongoService(collection_name=OTP_COLLECTION)
        record = service.custom_find_one({"phone": phone})

        if not record:
            print("No OTP found for this phone.")
            return False

        expires_at = record.get("expires_at")
        # Convert to datetime if it's a dict
        if isinstance(expires_at, dict) and "$date" in expires_at:
            expires_at = datetime.fromisoformat(expires_at["$date"].replace("Z", "+00:00"))
            
        if datetime.now(timezone.utc) > expires_at:
            print("OTP expired. Deleting it.")
            service.custom_delete_one({"phone": phone})
            return False
        
        # if record.get("attempts", 0) >= 5:
        #     print("Too many failed attempts.")
        #     return False

        if record.get("otp") == user_input:
            print("OTP verified. Deleting it.")
            # service.custom_delete_one({"phone": phone})
            return True

        else:
            service.collection.update_one({"phone": phone}, {"$inc": {"attempts": 1}})
            print("Incorrect OTP.")
            return False
