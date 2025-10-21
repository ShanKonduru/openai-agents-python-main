"""
Real AI Content Creation API Server
Uses actual OpenAI API for content generation
"""

import asyncio
import concurrent.futures
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
import openai

# Data models
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

# Load OpenAI API key
def load_openai_key():
    """Load OpenAI API key from file"""
    try:
        key_file = Path("openai_key.txt")
        if key_file.exists():
            api_key = key_file.read_text().strip()
            if api_key and api_key.startswith("sk-"):
                return api_key
            else:
                print("⚠️  Invalid API key format")
                return None
        else:
            print("⚠️  API key file not found")
            return None
    except Exception as e:
        print(f"⚠️  Error loading API key: {e}")
        return None

# Initialize OpenAI client
api_key = load_openai_key()
if api_key:
    openai.api_key = api_key
    # Create client with timeout settings
    client = openai.OpenAI(
        api_key=api_key,
        timeout=30.0,  # 30 second timeout
        max_retries=2   # Retry twice on failure
    )
    print("✅ OpenAI API key loaded successfully")
else:
    client = None
    print("❌ OpenAI API key not available - using mock responses")

# Create FastAPI app
app = FastAPI(
    title="AI Content Creation System",
    description="Real AI-powered content creation with OpenAI GPT",
    version="2.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for task status
task_storage: Dict[str, ProcessingStatus] = {}

# Conditionally serve React frontend static files
if os.path.exists("frontend/build/static"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the React frontend"""
    try:
        with open("frontend/build/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return HTMLResponse(f"""
        <html>
            <body>
                <h1>🤖 AI Content Creation System</h1>
                <p><strong>Status:</strong> Real AI system is running!</p>
                <p><strong>OpenAI API:</strong> {"✅ Connected" if client else "❌ Not available"}</p>
                <p><strong>For development:</strong> React app at http://localhost:3000</p>
                <p>API Documentation: <a href="/docs">http://localhost:8000/docs</a></p>
                <h2>Test API:</h2>
                <button onclick="testAPI()">Test API Connection</button>
                <div id="result"></div>
                <script>
                function testAPI() {{
                    fetch('/api/health')
                        .then(response => response.json())
                        .then(data => {{
                            document.getElementById('result').innerHTML = 
                                '<p style="color: green;">✅ API Response: ' + JSON.stringify(data) + '</p>';
                        }})
                        .catch(error => {{
                            document.getElementById('result').innerHTML = 
                                '<p style="color: red;">❌ API Error: ' + error + '</p>';
                        }});
                }}
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
        "message": "AI Content Creation API is running",
        "openai_available": client is not None,
        "mode": "production" if client else "development"
    }

async def call_openai_gpt(prompt: str, system_prompt: str = None) -> str:
    """Call OpenAI GPT with error handling"""
    if not client:
        return generate_fallback_content(prompt, "no_client")
    
    def _make_openai_call():
        """Synchronous OpenAI call to run in thread pool"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using the latest efficient model
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                timeout=25  # Additional timeout at request level
            )
            
            content = response.choices[0].message.content
            if content and content.strip():
                return content
            else:
                return generate_fallback_content(prompt, "empty_response")
                
        except openai.Timeout as e:
            print(f"OpenAI API Timeout: {e}")
            return generate_fallback_content(prompt, "timeout")
        except openai.RateLimitError as e:
            print(f"OpenAI Rate Limit: {e}")
            return generate_fallback_content(prompt, "rate_limit")
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return generate_fallback_content(prompt, "error", str(e))
    
    # Run the synchronous OpenAI call in a thread pool
    import concurrent.futures
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(executor, _make_openai_call),
                timeout=30.0  # Overall timeout for the entire operation
            )
            return result
        except asyncio.TimeoutError:
            print("OpenAI call timed out after 30 seconds")
            return generate_fallback_content(prompt, "timeout")

def generate_fallback_content(prompt: str, error_type: str, error_msg: str = "") -> str:
    """Generate meaningful fallback content when AI API fails"""
    topic_keywords = prompt.split()[:5]  # Get first few words as topic
    topic = " ".join(topic_keywords)
    
    if "research" in prompt.lower():
        return f"""# Research Summary: {topic}

## Key Points:
- Current trends and developments in {topic}
- Industry applications and use cases
- Benefits and challenges
- Future outlook and opportunities

## Key Statistics:
- Growing market interest in {topic}
- Increasing adoption across industries
- Emerging technologies and innovations

*Note: This is a simplified overview. For the most current information, please consult recent industry reports and academic sources.*"""

    elif "structure" in prompt.lower() or "outline" in prompt.lower():
        return f"""# Article Structure: {topic}

## Title Options:
- "Complete Guide to {topic}"
- "Understanding {topic}: A Comprehensive Overview"
- "Everything You Need to Know About {topic}"

## Article Outline:
1. **Introduction**
   - What is {topic}?
   - Why it matters today

2. **Core Concepts**
   - Fundamental principles
   - Key terminology

3. **Applications & Benefits**
   - Real-world use cases
   - Advantages and impact

4. **Implementation**
   - Getting started
   - Best practices

5. **Conclusion**
   - Key takeaways
   - Future considerations"""

    elif "image" in prompt.lower():
        return f"""# Image Concepts for {topic}

## 1. Header Image
- **Description**: Professional illustration showcasing {topic} concepts
- **Alt text**: "{topic} overview illustration"
- **Placement**: Top of article

## 2. Concept Diagram
- **Description**: Flowchart or diagram explaining {topic} process
- **Alt text**: "{topic} process diagram"
- **Placement**: After introduction

## 3. Practical Example
- **Description**: Screenshot or example of {topic} in action
- **Alt text**: "{topic} practical example"
- **Placement**: Mid-article

## 4. Summary Infographic
- **Description**: Visual summary of key points about {topic}
- **Alt text**: "{topic} key points infographic"
- **Placement**: Before conclusion"""

    elif "seo" in prompt.lower():
        return f"""# SEO Optimization for {topic}

## Title Variations:
1. "Complete Guide to {topic} in 2025"
2. "Understanding {topic}: Expert Tips & Best Practices"
3. "{topic} Explained: Everything You Need to Know"

## Meta Description:
"Comprehensive guide to {topic}. Learn key concepts, applications, and best practices from industry experts."

## Keywords:
- Primary: {topic.lower()}
- Secondary: {topic.lower()} guide, {topic.lower()} tips, {topic.lower()} best practices

## Content Improvements:
- Add more practical examples
- Include case studies
- Update with current trends
- Add call-to-action sections"""

    else:
        # Default article content
        return f"""# Complete Guide to {topic}

## Introduction
{topic} is an important subject that affects many aspects of modern life. Understanding its principles and applications can provide valuable insights for both personal and professional development.

## What is {topic}?
{topic} encompasses a range of concepts and practices that have evolved significantly over recent years. Its importance continues to grow as technology and society advance.

## Key Benefits
- Improved understanding of complex concepts
- Practical applications in various fields
- Enhanced decision-making capabilities
- Better preparation for future developments

## Applications
{topic} finds applications across multiple industries and use cases:

### Industry Applications
- Technology sector implementations
- Business process improvements
- Educational and training programs
- Research and development initiatives

### Practical Use Cases
- Daily workflow optimization
- Strategic planning and analysis
- Innovation and creative problem-solving
- Long-term sustainable practices

## Best Practices
To effectively implement {topic}, consider these recommendations:

1. **Start with fundamentals**: Build a solid foundation of understanding
2. **Stay updated**: Keep current with latest developments and trends
3. **Practice regularly**: Apply concepts in real-world scenarios
4. **Learn from others**: Engage with community and expert resources

## Getting Started
Begin your journey with {topic} by:
- Researching current industry standards
- Identifying relevant tools and resources
- Connecting with experts and practitioners
- Setting clear goals and objectives

## Conclusion
{topic} represents a valuable area of knowledge that continues to evolve. By understanding its principles and staying informed about developments, you can leverage its benefits for personal and professional growth.

The future of {topic} looks promising, with new opportunities emerging regularly. Consider this guide as a starting point for deeper exploration and practical application.

---
*This content was generated as a fallback due to API limitations. For the most current and detailed information, please consult recent expert sources and industry publications.*"""

@app.post("/api/content/create")
async def create_content(input_data: UserInput, background_tasks: BackgroundTasks):
    """Start AI content creation process"""
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_status = ProcessingStatus(
            task_id=task_id,
            status="processing",
            current_step=1,
            current_operation="🔍 Starting AI research..."
        )
        task_storage[task_id] = task_status
        
        # Start background AI processing
        background_tasks.add_task(process_ai_content_creation, task_id, input_data)
        
        return {"task_id": task_id, "status": "started"}
        
    except Exception as e:
        print(f"Error starting content creation: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start content creation: {str(e)}")

async def process_ai_content_creation(task_id: str, input_data: UserInput):
    """Background task with real AI content creation"""
    try:
        print(f"🚀 Starting content creation for task {task_id}")
        
        # Step 1: AI Research
        task_storage[task_id].current_operation = f"🔍 AI researching '{input_data.topic}'..."
        print(f"Step 1: Research for {input_data.topic}")
        await asyncio.sleep(1)
        
        research_prompt = f"""Research the topic "{input_data.topic}" and provide:
1. Key facts and current trends
2. Main subtopics to cover
3. Target audience considerations for {input_data.audience}
4. 3-5 important points to highlight

Keep it concise but comprehensive."""

        research_result = await call_openai_gpt(
            research_prompt,
            "You are an expert researcher. Provide accurate, up-to-date information."
        )
        print(f"✅ Research completed: {len(research_result)} characters")
        
        # Step 2: Content Structure
        task_storage[task_id].current_step = 2
        task_storage[task_id].current_operation = "📝 AI creating content structure..."
        print("Step 2: Creating structure")
        await asyncio.sleep(1)
        
        structure_prompt = f"""Based on this research: {research_result[:500]}...
        
Create a detailed outline for an article about "{input_data.topic}" with:
- Compelling title
- Introduction hook
- 3-5 main sections with subsections
- Conclusion strategy
- Target audience: {input_data.audience}
- Writing style: {input_data.style}
- Length: {input_data.length}"""

        structure_result = await call_openai_gpt(
            structure_prompt,
            "You are a content strategist. Create engaging, well-structured outlines."
        )
        print(f"✅ Structure completed: {len(structure_result)} characters")
        
        # Step 3: Full Article Creation
        task_storage[task_id].current_step = 3
        task_storage[task_id].current_operation = "✍️ AI writing full article..."
        print("Step 3: Writing article")
        await asyncio.sleep(2)
        
        article_prompt = f"""Write a complete article about "{input_data.topic}" using this structure:
{structure_result[:800]}...

Requirements:
- Target audience: {input_data.audience}
- Writing style: {input_data.style}
- Length: {input_data.length}
- Include practical examples
- Make it engaging and informative
- Use markdown formatting
- Add relevant headers and subheaders"""

        article_result = await call_openai_gpt(
            article_prompt,
            f"You are an expert {input_data.style.lower()} writer. Create high-quality content that engages {input_data.audience.lower()} readers."
        )
        print(f"✅ Article completed: {len(article_result)} characters")
        
        # Step 4: Image Descriptions
        task_storage[task_id].current_step = 4
        task_storage[task_id].current_operation = "🖼️ AI generating image concepts..."
        print("Step 4: Creating image concepts")
        await asyncio.sleep(1)
        
        image_prompt = f"""Based on this article about "{input_data.topic}":
{article_result[:500]}...

Create 3-4 detailed image descriptions that would enhance this article:
1. A main header image
2. Supporting diagrams or illustrations
3. Practical examples or screenshots
4. Infographic concepts

For each image, provide:
- Description for image generation
- Alt text for accessibility
- Placement suggestion in the article"""

        image_result = await call_openai_gpt(
            image_prompt,
            "You are a visual content strategist. Create compelling image concepts that enhance written content."
        )
        print(f"✅ Image concepts completed: {len(image_result)} characters")
        
        # Step 5: SEO & Final Polish
        task_storage[task_id].current_step = 5
        task_storage[task_id].current_operation = "🚀 AI optimizing for SEO and final polish..."
        print("Step 5: SEO optimization")
        await asyncio.sleep(1)
        
        seo_prompt = f"""Optimize this article for SEO and provide final recommendations:

Article: {article_result[:500]}...

Provide:
1. SEO-optimized title variations (3-4 options)
2. Meta description (155 characters max)
3. Primary and secondary keywords
4. Content improvements for better engagement
5. Call-to-action suggestions"""

        seo_result = await call_openai_gpt(
            seo_prompt,
            "You are an SEO expert. Optimize content for search engines while maintaining readability."
        )
        print(f"✅ SEO optimization completed: {len(seo_result)} characters")
        
        # Create final result
        final_result = {
            "title": f"AI-Generated Guide: {input_data.topic}",
            "content": article_result,
            "word_count": len(article_result.split()),
            "research_data": research_result,
            "structure_outline": structure_result,
            "image_concepts": image_result,
            "seo_optimization": seo_result,
            "metadata": {
                "topic": input_data.topic,
                "audience": input_data.audience,
                "style": input_data.style,
                "length": input_data.length,
                "created_at": datetime.now().isoformat(),
                "ai_model": "gpt-4o-mini" if client else "mock"
            }
        }
        
        # Update task status to completed
        task_storage[task_id].status = "completed"
        task_storage[task_id].current_operation = "✅ AI content creation completed!"
        task_storage[task_id].final_result = final_result
        print(f"🎉 Content creation completed for task {task_id}")
        
    except Exception as e:
        print(f"❌ Error in AI content creation for task {task_id}: {e}")
        import traceback
        traceback.print_exc()
        task_storage[task_id].status = "error"
        task_storage[task_id].error = f"AI processing failed: {str(e)}"

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
    print("🤖 Starting AI Content Creation System...")
    print(f"🔑 OpenAI API: {'✅ Connected' if client else '❌ Not available'}")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend will be at: http://localhost:8000")
    print("💡 Press Ctrl+C to stop")
    
    uvicorn.run(
        "real_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )