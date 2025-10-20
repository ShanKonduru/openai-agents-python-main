"""
Simple Test API Server for Content Creation System
Basic endpoints without agents integration for testing
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
import os

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Basic data models
class UserInput(BaseModel):
    topic: str
    audience: str = "General"
    style: str = "Professional"
    length: str = "Medium"

class ProcessingStatus(BaseModel):
    task_id: str
    status: str  # "processing", "completed", "error"
    current_step: int
    current_operation: str
    step_results: Optional[Dict[int, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="Content Creation System API",
    description="Backend API for the AI-powered content creation system",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for task status (in production, use Redis or database)
task_storage: Dict[str, ProcessingStatus] = {}

# Conditionally serve React frontend static files (only if build exists)
if os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the React frontend"""
    try:
        with open("frontend/build/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <body>
                <h1>Content Creation System - Test Mode</h1>
                <p><strong>Status:</strong> Backend API is running successfully!</p>
                <p><strong>For development:</strong> Start React dev server separately on port 3000</p>
                <p><strong>For production:</strong> Build the frontend first:</p>
                <pre>cd frontend && npm install && npm run build</pre>
                <p>API Documentation: <a href="/docs">http://localhost:8000/docs</a></p>
                <h2>Test API:</h2>
                <button onclick="testAPI()">Test API Connection</button>
                <div id="result"></div>
                <script>
                function testAPI() {
                    fetch('/api/health')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('result').innerHTML = 
                                '<p style="color: green;">✅ API Response: ' + JSON.stringify(data) + '</p>';
                        })
                        .catch(error => {
                            document.getElementById('result').innerHTML = 
                                '<p style="color: red;">❌ API Error: ' + error + '</p>';
                        });
                }
                </script>
            </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Content Creation API is running"
    }

@app.post("/api/content/create")
async def create_content(input_data: UserInput, background_tasks: BackgroundTasks):
    """Start content creation process"""
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_status = ProcessingStatus(
            task_id=task_id,
            status="processing",
            current_step=1,
            current_operation="Initializing content creation process..."
        )
        task_storage[task_id] = task_status
        
        # Start background processing
        background_tasks.add_task(process_content_creation, task_id, input_data)
        
        return {"task_id": task_id, "status": "started"}
        
    except Exception as e:
        print(f"Error starting content creation: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start content creation: {str(e)}")

async def process_content_creation(task_id: str, input_data: UserInput):
    """Background task to process content creation (mock implementation)"""
    try:
        task_storage[task_id].current_operation = "Researching topic..."
        await asyncio.sleep(2)  # Simulate research time
        
        task_storage[task_id].current_step = 2
        task_storage[task_id].current_operation = "Creating content structure..."
        await asyncio.sleep(2)  # Simulate content creation
        
        task_storage[task_id].current_step = 3
        task_storage[task_id].current_operation = "Formatting content..."
        await asyncio.sleep(1)  # Simulate formatting
        
        task_storage[task_id].current_step = 4
        task_storage[task_id].current_operation = "Creating image descriptions..."
        await asyncio.sleep(1)  # Simulate image processing
        
        task_storage[task_id].current_step = 5
        task_storage[task_id].current_operation = "Finalizing article..."
        await asyncio.sleep(1)  # Simulate final processing
        
        # Mock final result
        final_result = {
            "title": f"Complete Guide to {input_data.topic}",
            "content": f"This is a comprehensive article about {input_data.topic}. " +
                      f"Written for {input_data.audience} audience in {input_data.style} style.",
            "word_count": 1500,
            "images": [
                {"description": f"Main illustration for {input_data.topic}", "alt_text": f"{input_data.topic} overview"},
                {"description": f"Supporting diagram for {input_data.topic}", "alt_text": f"{input_data.topic} details"}
            ],
            "seo_keywords": [input_data.topic.lower(), "guide", "tutorial"],
            "created_at": datetime.now().isoformat()
        }
        
        # Update task status to completed
        task_storage[task_id].status = "completed"
        task_storage[task_id].current_operation = "Content creation completed!"
        task_storage[task_id].final_result = final_result
        
    except Exception as e:
        print(f"Error in content creation: {e}")
        traceback.print_exc()
        task_storage[task_id].status = "error"
        task_storage[task_id].error = str(e)

@app.get("/api/content/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a content creation task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_storage[task_id]

@app.get("/api/content/download/{task_id}")
async def download_content(task_id: str):
    """Download the completed content"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_status = task_storage[task_id]
    if task_status.status != "completed" or not task_status.final_result:
        raise HTTPException(status_code=400, detail="Content not ready for download")
    
    return task_status.final_result

if __name__ == "__main__":
    print("🚀 Starting Content Creation API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend will be at: http://localhost:8000")
    print("💡 Press Ctrl+C to stop")
    
    uvicorn.run(
        "test_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )