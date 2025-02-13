import os
import logging
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from backend.langgraph_agent import MasterAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('newspaper_generator.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
backend_app = FastAPI(
    title="Newspaper Generator API",
    description="API for generating AI-powered newspapers",
    version="1.0.0"
)

# Configure CORS
backend_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewspaperRequest(BaseModel):
    topics: List[str]
    layout: str

@backend_app.get("/")
async def index():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {"status": "Running"}

@backend_app.post("/generate_newspaper")
async def generate_newspaper(request: NewspaperRequest):
    """
    Generate a newspaper based on provided topics and layout
    """
    try:
        logger.info(f"Generate newspaper endpoint called with data: {request.dict()}")
        
        # Initialize master agent
        master_agent = MasterAgent()
        logger.info("MasterAgent initialized")
        
        # Process topics and generate newspaper
        logger.info(f"Processing topics: {request.topics}")
        newspaper_path = master_agent.run(request.topics, request.layout)
        logger.info(f"Generated newspaper at path: {newspaper_path}")
        
        return {"status": "success", "path": newspaper_path}
        
    except Exception as e:
        logger.error(f"Error generating newspaper: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Log all registered routes
logger.info("Registered Routes:")
for route in backend_app.routes:
    logger.info(f"{route.name}: {route.methods} - {route.path}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(backend_app, host="0.0.0.0", port=9000)

