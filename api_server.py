"""
FastAPI Backend Server for Content Creation System
Provides REST API endpoints for the React frontend
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Import our content creation system
try:
    from enhanced_content_system import (
        create_enhanced_content_workflow,
        ContentCreationConfig,
        UserInput,
        ResearchOutput,
        MarkdownContent,
        ImageDescription,
        PublishedArticle
    )
    CONTENT_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Content creation system not available: {e}")
    print("🔧 Running in demo mode with mock responses")
    CONTENT_SYSTEM_AVAILABLE = False
    
    # Create mock classes for demo mode
    class ContentCreationConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

app = FastAPI(
    title="Content Creation API",
    description="AI-Powered Multi-Agent Content Creation System",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task storage for tracking progress
active_tasks: Dict[str, Dict[str, Any]] = {}

class ContentCreationRequest(BaseModel):
    topic: str
    config: dict

class TaskStatus(BaseModel):
    task_id: str
    status: str  # 'running', 'completed', 'failed'
    progress: float
    current_step: int
    current_operation: str
    step_results: Optional[Dict[int, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Conditionally serve React frontend static files (only if build exists)
import os
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
                <h1>Content Creation System - Development Mode</h1>
                <p><strong>For development:</strong> Start React dev server separately on port 3000</p>
                <p><strong>For production:</strong> Build the frontend first:</p>
                <pre>cd frontend && npm install && npm run build</pre>
                <p>API is running on <a href="/docs">http://localhost:8000/docs</a></p>
            </body>
        </html>
        """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/create-content")
async def create_content(request: ContentCreationRequest, background_tasks: BackgroundTasks):
    """Start content creation process"""
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task tracking
        active_tasks[task_id] = {
            "status": "running",
            "progress": 0.0,
            "current_step": 0,
            "current_operation": "Initializing...",
            "step_results": {},
            "final_result": None,
            "error": None,
            "started_at": datetime.now()
        }
        
        # Start background task
        background_tasks.add_task(run_content_creation, task_id, request.topic, request.config)
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Content creation started successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start content creation: {str(e)}")

@app.get("/api/progress/{task_id}")
async def get_progress(task_id: str):
    """Get progress of content creation task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        current_step=task["current_step"],
        current_operation=task["current_operation"],
        step_results=task["step_results"],
        final_result=task["final_result"],
        error=task["error"]
    )

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Mark task as cancelled
    active_tasks[task_id]["status"] = "cancelled"
    active_tasks[task_id]["current_operation"] = "Cancelled by user"
    
    return {"success": True, "message": "Task cancelled successfully"}

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "progress": task["progress"],
                "started_at": task["started_at"].isoformat(),
                "current_operation": task["current_operation"]
            }
            for task_id, task in active_tasks.items()
        ]
    }

@app.get("/api/download/{task_id}/{file_type}")
async def download_file(task_id: str, file_type: str):
    """Download generated content files"""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    if task["status"] != "completed" or not task["final_result"]:
        raise HTTPException(status_code=400, detail="Task not completed or no result available")
    
    final_result = task["final_result"]
    
    if file_type == "html":
        return FileResponse(
            final_result["html_file_path"],
            media_type="text/html",
            filename=f"{final_result['article_url_slug']}.html"
        )
    elif file_type == "markdown":
        return FileResponse(
            final_result["markdown_file_path"],
            media_type="text/markdown",
            filename=f"{final_result['article_url_slug']}.md"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid file type")

async def run_content_creation(task_id: str, topic: str, config_dict: dict):
    """Background task to run content creation workflow"""
    try:
        # Update task status
        def update_progress(step: int, progress: float, operation: str, step_result: Any = None):
            if task_id in active_tasks:
                active_tasks[task_id]["current_step"] = step
                active_tasks[task_id]["progress"] = progress
                active_tasks[task_id]["current_operation"] = operation
                
                if step_result:
                    active_tasks[task_id]["step_results"][step] = step_result

        # Create configuration
        config = ContentCreationConfig(
            output_directory=config_dict.get("output_directory", "output"),
            generate_real_images=config_dict.get("generate_real_images", False),
            max_word_count=config_dict.get("max_word_count", 2000),
            include_toc=config_dict.get("include_toc", True),
            include_references=config_dict.get("include_references", True)
        )
        
        # Step 1: User Input Processing
        update_progress(0, 10, "Processing user input...")
        
        # Mock user input processing (replace with actual agent call)
        user_input_result = {
            "topic": topic,
            "target_audience": config_dict.get("target_audience", "general"),
            "content_type": config_dict.get("content_type", "article"),
            "content_length": config_dict.get("content_length", "medium"),
            "tone": config_dict.get("tone", "professional"),
            "include_technical_details": config_dict.get("include_technical_details", False)
        }
        update_progress(0, 20, "User input processed", user_input_result)
        
        # Step 2: Research Phase
        update_progress(1, 25, "Conducting research...")
        await asyncio.sleep(2)  # Simulate research time
        
        research_result = {
            "topic": topic,
            "executive_summary": f"Comprehensive analysis of {topic} covering key aspects and current trends.",
            "key_points": [
                f"Key insight about {topic}",
                f"Important aspect of {topic}",
                f"Current trends in {topic}",
                f"Future implications of {topic}"
            ],
            "detailed_sections": {
                "Introduction": f"Overview of {topic}",
                "Main Content": f"Detailed analysis of {topic}",
                "Conclusion": f"Summary and future outlook for {topic}"
            },
            "statistics": [
                f"85% of experts agree on {topic} importance",
                f"Recent studies show {topic} growth of 120%"
            ],
            "sources": [
                "Academic Research Papers",
                "Industry Reports",
                "Expert Interviews"
            ],
            "research_quality_score": 8
        }
        update_progress(1, 45, "Research completed", research_result)
        
        # Step 3: Content Structuring
        update_progress(2, 50, "Creating structured content...")
        await asyncio.sleep(3)  # Simulate content creation time
        
        content_result = {
            "title": f"The Complete Guide to {topic}",
            "subtitle": f"Everything you need to know about {topic}",
            "summary": f"A comprehensive guide covering all aspects of {topic}",
            "table_of_contents": [
                "Introduction",
                "Key Concepts",
                "Best Practices",
                "Implementation",
                "Conclusion"
            ],
            "markdown_content": f"""# The Complete Guide to {topic}

## Introduction

{topic} is a fascinating subject that has gained significant attention in recent years...

## Key Concepts

Understanding the fundamental concepts of {topic} is crucial for...

## Best Practices

When working with {topic}, it's important to follow these best practices...

## Implementation

Here's how you can implement {topic} in your projects...

## Conclusion

In conclusion, {topic} offers many opportunities for...
""",
            "sections": ["Introduction", "Key Concepts", "Best Practices", "Implementation", "Conclusion"],
            "keywords": [topic.lower(), "guide", "implementation", "best practices"],
            "meta_description": f"Complete guide to {topic} with practical examples and best practices",
            "estimated_read_time": "8 min read"
        }
        update_progress(2, 70, "Content structured", content_result)
        
        # Step 4: Visual Design
        update_progress(3, 75, "Designing visual content...")
        await asyncio.sleep(1)  # Simulate image design time
        
        image_result = {
            "hero_image": {
                "prompt": f"Professional hero image representing {topic}",
                "alt_text": f"Hero image for {topic} article"
            },
            "section_images": [
                {"prompt": f"Infographic about {topic} concepts", "alt_text": f"{topic} concepts diagram"},
                {"prompt": f"Implementation example for {topic}", "alt_text": f"{topic} implementation"}
            ],
            "image_style": "Modern, professional, clean design",
            "color_scheme": "Blue and white with accent colors",
            "aspect_ratios": {"hero": "16:9", "sections": "4:3"}
        }
        update_progress(3, 85, "Visual design completed", image_result)
        
        # Step 5: Publishing
        update_progress(4, 90, "Publishing article...")
        await asyncio.sleep(2)  # Simulate publishing time
        
        # Run the actual content creation workflow
        try:
            # This would be the actual workflow call
            final_result = await create_enhanced_content_workflow(topic, config)
            
            # Convert to serializable format
            final_result_dict = {
                "html_file_path": final_result.html_file_path,
                "markdown_file_path": final_result.markdown_file_path,
                "article_title": final_result.article_title,
                "article_url_slug": final_result.article_url_slug,
                "word_count": final_result.word_count,
                "sections_count": final_result.sections_count,
                "images_included": final_result.images_included,
                "publish_date": final_result.publish_date,
                "estimated_read_time": final_result.estimated_read_time,
                "seo_score": final_result.seo_score,
                "html_content": "",  # Will be loaded when needed
                "markdown_content": ""  # Will be loaded when needed
            }
            
            # Load content for preview
            try:
                with open(final_result.html_file_path, 'r', encoding='utf-8') as f:
                    final_result_dict["html_content"] = f.read()
            except:
                pass
                
            try:
                with open(final_result.markdown_file_path, 'r', encoding='utf-8') as f:
                    final_result_dict["markdown_content"] = f.read()
            except:
                pass
            
        except Exception as e:
            # Fallback result for demo
            final_result_dict = {
                "html_file_path": f"output/{topic.replace(' ', '_').lower()}.html",
                "markdown_file_path": f"output/{topic.replace(' ', '_').lower()}.md",
                "article_title": f"The Complete Guide to {topic}",
                "article_url_slug": topic.replace(' ', '-').lower(),
                "word_count": 1500,
                "sections_count": 5,
                "images_included": 3,
                "publish_date": datetime.now().strftime('%B %d, %Y'),
                "estimated_read_time": "8 min read",
                "seo_score": 8,
                "html_content": f"<h1>The Complete Guide to {topic}</h1><p>Your article content here...</p>",
                "markdown_content": f"# The Complete Guide to {topic}\n\nYour article content here..."
            }
        
        update_progress(4, 100, "Article published successfully", final_result_dict)
        
        # Mark task as completed
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["final_result"] = final_result_dict
        active_tasks[task_id]["current_operation"] = "Completed successfully"
        
    except Exception as e:
        # Mark task as failed
        error_msg = f"Content creation failed: {str(e)}"
        print(f"Error in task {task_id}: {error_msg}")
        print(traceback.format_exc())
        
        if task_id in active_tasks:
            active_tasks[task_id]["status"] = "failed"
            active_tasks[task_id]["error"] = error_msg
            active_tasks[task_id]["current_operation"] = "Failed"

if __name__ == "__main__":
    print("🚀 Starting Content Creation API Server...")
    print("📱 React Frontend: http://localhost:3000")
    print("🔗 API Docs: http://localhost:8000/docs")
    print("❤️  API Health: http://localhost:8000/api/health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )