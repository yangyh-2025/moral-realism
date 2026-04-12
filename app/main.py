# FastAPI Application Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import api_router
import os

# Create FastAPI application
app = FastAPI(
    title="International Order ABM Simulation System",
    description="基于大语言模型的国际秩序ABM仿真系统 - 克莱因国力方程修订版V1.3",
    version="1.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """
    Root endpoint - returns system information
    """
    return {
        "system": "International Order ABM Simulation System",
        "version": "1.3.0",
        "description": "基于大语言模型的国际秩序ABM仿真系统",
        "status": "running",
        "docs": "/docs",
        "api_prefix": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "system": "International Order ABM"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
