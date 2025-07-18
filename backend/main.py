# Import necessary modules
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config
from api.routes import router as api_router

# Create FastAPI app
app = FastAPI(
    title="University AI Assistant Backend",
    version="1.0.0"
)

# Configure CORS for development (allow React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router under /api
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/")
def health_check():
    return {"status": "ok"}

# Run app via Uvicorn when executed directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=True  # for dev
    )
