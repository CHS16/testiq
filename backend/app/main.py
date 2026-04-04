from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import interactions

# Initialize FastAPI app
app = FastAPI(
    title="IntentIQ Backend API",
    description="Backend AI-powered robust call analysis system",
    version="1.0.0"
)

# CORS middleware for permitting cross-backend/frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production replace this with explicit origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application routers
app.include_router(interactions.router)

@app.get("/", tags=["Health"])
async def health_check():
    """
    Standard base health check endpoint to verify system uptime.
    """
    return {
        "status": "online", 
        "system": "IntentIQ",
        "message": "Welcome to IntentIQ backend API."
    }
