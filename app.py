from multiprocessing import Process
import logging
import time
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.server import backend_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

frontend_app = FastAPI()

# Configure CORS
frontend_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
frontend_app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@frontend_app.get("/")
async def index():
    return FileResponse('frontend/index.html')

@frontend_app.get("/favicon.ico")
async def favicon():
    return FileResponse('frontend/static/favicon.ico', media_type="image/x-icon")

@frontend_app.get("/{path:path}")
async def static_proxy(path: str):
    if path.startswith("static/"):
        return FileResponse(f'frontend/{path}')
    return FileResponse(f'frontend/{path}')

def wait_for_backend():
    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get('http://localhost:9000/')
            if response.status_code == 200:
                logger.info("Backend server is ready!")
                return True
        except requests.exceptions.ConnectionError:
            attempt += 1
            logger.info(f"Waiting for backend server... (attempt {attempt}/{max_attempts})")
            time.sleep(2)
    logger.error("Backend server failed to start!")
    return False

def run_frontend():
    logger.info("Starting frontend server on port 5000")
    uvicorn.run(frontend_app, host="0.0.0.0", port=5000)

def run_backend():
    logger.info("Starting backend server on port 9000")
    uvicorn.run(backend_app, host="0.0.0.0", port=9000)

if __name__ == '__main__':
    try:
        # Start the backend server
        logger.info("Starting backend server...")
        backend_process = Process(target=run_backend)
        backend_process.start()

        # Wait for backend to be ready
        if not wait_for_backend():
            logger.error("Failed to start backend server. Shutting down...")
            backend_process.terminate()
            exit(1)

        # Start the frontend server
        logger.info("Starting frontend server...")
        frontend_process = Process(target=run_frontend)
        frontend_process.start()

        # Join the processes
        frontend_process.join()
        backend_process.join()

    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
        frontend_process.terminate()
        backend_process.terminate()
        exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        try:
            frontend_process.terminate()
            backend_process.terminate()
        except:
            pass
        exit(1)
