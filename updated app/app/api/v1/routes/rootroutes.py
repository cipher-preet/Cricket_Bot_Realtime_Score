from fastapi import APIRouter
from app.api.v1 import cricket_routes
from app.api.v1.user import auth_routes, subscription_routes




router = APIRouter(
    prefix="/api/v1",        
    tags=["API v1"]
)





router.include_router(cricket_routes.router, prefix="/cricket_coversation")
router.include_router(auth_routes.router, prefix="/auth")



@router.get("/")
async def get_api_v1_root():
    return {"message": "Welcome to API v1!"}