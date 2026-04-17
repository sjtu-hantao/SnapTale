import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables, get_db
from app.api import router
import dotenv

dotenv.load_dotenv()

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parents[1]
MEDIA_DIR = BASE_DIR / "storage" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your FastAPI app setup code here
app.include_router(router)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.on_event("startup")
def startup_event():
    create_db_and_tables()


# Example of using the get_db function
@app.get("/")
async def root():
    db = next(get_db())
    # Use db to query your database
    return {"message": "Welcome to VMBook!"}

import logging

@app.middleware("http") 
async def log_requests(request: Request, call_next): 
    logger = logging.getLogger(__name__)
    logger.info(f"Request: {request.method} {request.url}") 
    logger.info(f"Headers: {request.headers}") 
    body = await request.body() 
    logger.info(f"Body: {body}") 
    response = await call_next(request) 
    logger.info(f"Response status: {response.status_code}") 
    return response

if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # or run with `uvicorn main:app --reload --host 0.0.0.0` in the terminal
    
