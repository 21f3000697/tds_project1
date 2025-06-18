from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import base64
import json
import time
import psutil
import os
from utils_lightweight import LightweightTDSVirtualTA

app = FastAPI(title="TDS Virtual TA API (Lightweight)", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image

class QueryResponse(BaseModel):
    answer: str
    links: List[Dict[str, str]]

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# Initialize the lightweight virtual TA system
print("Initializing Lightweight TDS Virtual TA...")
print(f"Initial memory usage: {get_memory_usage():.2f} MB")
virtual_ta = LightweightTDSVirtualTA()
print(f"Memory usage after initialization: {get_memory_usage():.2f} MB")
print("Lightweight TDS Virtual TA initialized successfully!")

@app.post("/api/", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Answer student questions based on TDS course content and discourse posts.
    Memory-efficient implementation using keyword-based search.
    
    Args:
        request: Contains the question and optional base64 image
        
    Returns:
        JSON response with answer and relevant links
    """
    start_time = time.time()
    
    try:
        # Validate request
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Process the question (with or without image)
        answer, links = virtual_ta.answer_question(
            question=request.question.strip(),
            image_base64=request.image
        )
        
        # Check if response time is within 30 seconds
        response_time = time.time() - start_time
        if response_time > 30:
            print(f"Warning: Response took {response_time:.2f} seconds")
        
        return QueryResponse(answer=answer, links=links)
        
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint with memory usage"""
    memory_usage = get_memory_usage()
    return {
        "status": "healthy", 
        "message": "TDS Virtual TA is running",
        "memory_usage_mb": round(memory_usage, 2),
        "memory_limit_mb": 512
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    memory_usage = get_memory_usage()
    return {
        "message": "TDS Virtual TA API (Lightweight)",
        "version": "1.0.0",
        "memory_usage_mb": round(memory_usage, 2),
        "endpoints": {
            "POST /api/": "Submit a question (with optional image)",
            "GET /health": "Health check with memory usage",
            "GET /": "API information"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable for Render deployment
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 