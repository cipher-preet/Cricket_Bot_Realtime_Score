from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.routes import rootroutes
from fastapi import FastAPI, Request
import logging
import os


logger = logging.getLogger("uvicorn.error")


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://192.168.29.43"
]

app = FastAPI(
    title="Stumpzy API",
    description="API for Stumpzy, a cricket-related application",
    version="1.0.0",
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "a_very_long_and_random_string_here_for_dev")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"Error processing request {request.url}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


app.include_router(rootroutes.router)