from fastapi import APIRouter
from app.api.routes import complaints

api_router = APIRouter()
api_router.include_router(complaints.router)
