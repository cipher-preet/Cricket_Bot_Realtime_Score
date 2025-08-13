from fastapi import APIRouter, Response, Request, HTTPException
import traceback
from fastapi.responses import JSONResponse
from app.models.foundational_model import userModel, LoginModel, otpModel
from app.api.repository.mongo_repo import Userdetails
# from authlib.integrations.starlette_client import OAuth
# import os



router = APIRouter(tags=["auth"])

# oauth = OAuth()





# Configure Google OAuth
# oauth.register(
#     name='google',
#     client_id=os.getenv("GOOGLE_CLIENT_ID"),
#     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={'scope': 'openid email profile'},
#     redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
# )

# all routes


# @router.post("/registeruser",summary="Register new user", description="Register the new user to database")
# async def registeruser(data : userModel):
#     try:
#         userauth = Userdetails()
#         userauth.registernewuser(data)
#         return JSONResponse(
#             status_code=200, content={"success": True, "message": "user registered successfully"}
#         )
#     except Exception as e:
#         print(traceback.format_exc())
#         return JSONResponse(status_code=500, content= {"success": False, "message": str(e)})
    


# google authentication handling

# @router.get('/google/login', summary="Initiate Google OAuth login")
# async def login_google(request: Request):
#     """
#     Redirects the user to Google's authentication page.
#     """
#     # prevent CSRF attacks
#     state = generate_token(20)
#     redirect_uri = request.url_for('auth_google_callback')
#     request.session['oauth_state'] = state 
#     redirect_uri = await oauth.create_client('google').authorize_redirect(request, redirect_uri=redirect_uri, state=state)
#     return redirect_uri






# @router.get('/google/callback', summary="Google OAuth callback endpoint")
# async def auth_google_callback(request: Request):
#     stored_state = request.session.pop('oauth_state', None)
    
#     print("stored state", stored_state)
#     if not stored_state or stored_state != request.query_params.get('state'):
#         raise HTTPException(status_code=400, detail="CSRF state mismatch or missing.")

#     try:
#         token = await oauth.create_client('google').authorize_access_token(request)

#         userinfo = token.get('userinfo')
        
        
#         print("this is userinfo : :::::::::::::::::::::::::::::::::", userinfo)
#         if not userinfo:
#             raise HTTPException(status_code=400, detail="Failed to get user info from Google ID token.")
#         userauth = Userdetails()
#         response = userauth.googleauthentication(request=request, userinfo=userinfo)
#         print("response", response)
#         return JSONResponse(
#             status_code=200,
#             content=str(response)
#         )

#     except Exception as e:
#         print(traceback.format_exc())
#         return JSONResponse(status_code=500, content= {"success": False, "message": str(e)})

@router.post("/sendotptouser", summary="Send OTP to user", description="Api to send otp to user for verification")
def sendotptouser(phone: otpModel):
    try:
        print("Received phone number:", phone)
        if not phone:
            raise HTTPException(status_code=400, detail="Phone number is required.")
        
        userauth = Userdetails()
        message =  userauth.send_user_otp(phone = phone.model_dump().get("phone_number"))
        return JSONResponse(
            status_code=200, content={"success": True, "message": message["message"]}
        )
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})

@router.post("/verifyandloginuser",summary="login to stumpzy", description="Api to login to stumpzy dashboard")
def verifyandloginuser(logindetails: LoginModel, response: Response ):
    try:
        userauth = Userdetails()
        return userauth.verify_and_login_user(logindetails, response)
        # return JSONResponse(
        #     status_code=200, content={"success": True, "message": "user registered successfully"}
        # )
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content= {"success": False, "message": str(e)})
    
    
@router.post("/userlogout",summary="logout from stumpzy", description="Api to logout the user from stumpzy dashboard")
def logoutuser( response: Response ):
    try:

        response.delete_cookie(key="user_id")
        # return userauth.login_user(logindetails, response)
        return JSONResponse(
            status_code=200, content={"success": True, "message": "user logged out successfully"}
        )
    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content= {"success": False, "message": str(e)})


