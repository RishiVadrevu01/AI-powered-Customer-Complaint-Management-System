from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.main import api_router

# Create database tables automatically on launch
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Interactive Swagger API Documentation for AIVOA AI-Powered Customer Complaint Management System",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", include_in_schema=False)
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "Operational",
        "swagger_docs": "http://localhost:8000/docs",
        "redoc_docs": "http://localhost:8000/redoc",
        "api_v1": f"{settings.API_V1_STR}/complaints"
    }
