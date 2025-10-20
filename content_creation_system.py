"""
Multi-Agent Content Creation System
===================================

This system creates interactive HTML articles with images from user topics.

Agent Flow:
1. User Input Agent - Takes and validates user input
2. Research Agent - Researches the given topic
3. Markdown Agent - Converts research to structured markdown
4. Image Agent - Generates suitable images based on content
5. Publisher Agent - Creates interactive HTML page with content and images
"""

import asyncio
import os
import json
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from agents import Agent, Runner, function_tool, trace
from pydantic import BaseModel, Field


# ========================= DATA MODELS =========================


class UserInput(BaseModel):
    """User input validation model"""

    topic: str = Field(description="The topic to research and create content about")
    target_audience: str = Field(
        default="general", description="Target audience for the content"
    )
    content_length: str = Field(
        default="medium", description="Desired content length: short, medium, long"
    )
    include_technical_details: bool = Field(
        default=False, description="Whether to include technical details"
    )


class ResearchOutput(BaseModel):
    """Research agent output model"""

    topic: str
    key_points: List[str] = Field(description="Key points discovered during research")
    detailed_information: str = Field(description="Detailed research findings")
    sources: List[str] = Field(description="Research sources and references")
    related_topics: List[str] = Field(
        description="Related topics for further exploration"
    )


class MarkdownContent(BaseModel):
    """Markdown agent output model"""

    title: str = Field(description="Article title")
    summary: str = Field(description="Brief summary of the content")
    markdown_content: str = Field(description="Full markdown formatted content")
    sections: List[str] = Field(description="List of main sections")
    keywords: List[str] = Field(description="Important keywords for SEO")


class ImageDescription(BaseModel):
    """Image generation description model"""

    main_image_prompt: str = Field(description="Prompt for the main hero image")
    section_images: List[str] = Field(description="Prompts for section images")
    image_style: str = Field(
        description="Style guide for images (realistic, artistic, etc.)"
    )


class PublishedArticle(BaseModel):
    """Final published article model"""

    html_file_path: str = Field(description="Path to the generated HTML file")
    article_title: str
    word_count: int
    sections_count: int
    images_included: int
    publish_date: str


# ========================= UTILITY FUNCTIONS =========================


@function_tool
def save_file(content: str, filename: str, directory: str = "output") -> str:
    """Save content to a file in the specified directory"""
    output_dir = Path(directory)
    output_dir.mkdir(exist_ok=True)

    file_path = output_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(file_path.absolute())


@function_tool
def create_html_template(title: str, content: str, image_urls: List[str] = None) -> str:
    """Create an interactive HTML template with the content"""
    if image_urls is None:
        image_urls = []

    # Create image gallery HTML
    image_gallery = ""
    if image_urls:
        image_gallery = """
        <div class="image-gallery">
            <h3>Related Images</h3>
            <div class="gallery-grid">
        """
        for i, url in enumerate(image_urls):
            image_gallery += f"""
                <div class="gallery-item">
                    <img src="{url}" alt="Article Image {i+1}" onclick="openModal(this)">
                </div>
            """
        image_gallery += """
            </div>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header .date {{
                opacity: 0.9;
                font-size: 1.1em;
            }}
            
            .content {{
                padding: 40px 30px;
            }}
            
            .content h1, .content h2, .content h3 {{
                color: #2c3e50;
                margin-top: 30px;
                margin-bottom: 15px;
            }}
            
            .content h1 {{
                font-size: 2em;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }}
            
            .content h2 {{
                font-size: 1.6em;
                color: #34495e;
            }}
            
            .content h3 {{
                font-size: 1.3em;
                color: #7f8c8d;
            }}
            
            .content p {{
                margin-bottom: 20px;
                text-align: justify;
                font-size: 1.1em;
            }}
            
            .content ul, .content ol {{
                margin-left: 20px;
                margin-bottom: 20px;
            }}
            
            .content li {{
                margin-bottom: 8px;
                font-size: 1.05em;
            }}
            
            .content blockquote {{
                border-left: 4px solid #667eea;
                padding-left: 20px;
                margin: 20px 0;
                font-style: italic;
                background: #f8f9fa;
                padding: 15px 20px;
                border-radius: 5px;
            }}
            
            .content code {{
                background: #f1f3f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            
            .content pre {{
                background: #f1f3f4;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 20px 0;
            }}
            
            .image-gallery {{
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #ecf0f1;
            }}
            
            .gallery-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .gallery-item img {{
                width: 100%;
                height: 200px;
                object-fit: cover;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .gallery-item img:hover {{
                transform: scale(1.05);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }}
            
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.9);
            }}
            
            .modal-content {{
                margin: auto;
                display: block;
                width: 80%;
                max-width: 700px;
                max-height: 80%;
                margin-top: 5%;
            }}
            
            .close {{
                position: absolute;
                top: 15px;
                right: 35px;
                color: #f1f1f1;
                font-size: 40px;
                font-weight: bold;
                cursor: pointer;
            }}
            
            .close:hover {{
                color: #bbb;
            }}
            
            .footer {{
                background: #2c3e50;
                color: white;
                text-align: center;
                padding: 20px;
                font-size: 0.9em;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    margin: 10px;
                    border-radius: 10px;
                }}
                
                .header {{
                    padding: 30px 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .gallery-grid {{
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <div class="date">Published on {datetime.now().strftime('%B %d, %Y')}</div>
            </div>
            
            <div class="content">
                {content}
                {image_gallery}
            </div>
            
            <div class="footer">
                Generated by Multi-Agent Content Creation System | 
                Powered by OpenAI Agents SDK
            </div>
        </div>
        
        <!-- Modal for image viewing -->
        <div id="imageModal" class="modal">
            <span class="close" onclick="closeModal()">&times;</span>
            <img class="modal-content" id="modalImage">
        </div>
        
        <script>
            function openModal(img) {{
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                modal.style.display = 'block';
                modalImg.src = img.src;
            }}
            
            function closeModal() {{
                document.getElementById('imageModal').style.display = 'none';
            }}
            
            // Close modal when clicking outside the image
            document.getElementById('imageModal').onclick = function(event) {{
                if (event.target === this) {{
                    closeModal();
                }}
            }}
            
            // Close modal with Escape key
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape') {{
                    closeModal();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_template


# ========================= AGENT DEFINITIONS =========================

# 1. User Input Agent
user_input_agent = Agent[None](
    name="User Input Agent",
    instructions="""You are a user input validation agent. Your job is to:
    1. Take user input about a topic they want content created for
    2. Ask clarifying questions if needed
    3. Validate and structure the input properly
    4. Ensure the topic is appropriate and feasible for content creation
    
    Always be helpful and guide users toward providing clear, actionable topics.
    """,
    output_type=UserInput,
)

# 2. Research Agent
research_agent = Agent[None](
    name="Research Agent",
    instructions="""You are a comprehensive research agent. Your job is to:
    1. Research the given topic thoroughly
    2. Gather key points, detailed information, and insights
    3. Identify credible sources and references
    4. Find related topics that might interest readers
    
    Provide well-structured, accurate, and comprehensive research that can be used 
    to create high-quality content. Focus on current information and multiple perspectives.
    """,
    output_type=ResearchOutput,
)

# 3. Markdown Conversion Agent
markdown_agent = Agent[None](
    name="Markdown Agent",
    instructions="""You are a content structuring agent. Your job is to:
    1. Take research output and convert it into well-structured markdown
    2. Create engaging titles and clear section headers
    3. Format content with proper markdown syntax
    4. Include lists, quotes, and other formatting as appropriate
    5. Generate SEO-friendly keywords
    
    Create content that is engaging, well-organized, and easy to read.
    Use proper markdown formatting including headers, lists, emphasis, and code blocks where appropriate.
    """,
    output_type=MarkdownContent,
)

# 4. Image Description Agent
image_agent = Agent[None](
    name="Image Agent",
    instructions="""You are an image description agent. Your job is to:
    1. Analyze the content and create detailed image prompts
    2. Design a main hero image that captures the essence of the topic
    3. Create prompts for section images that support the content
    4. Specify appropriate image styles (realistic, artistic, infographic, etc.)
    
    Create detailed, specific prompts that would result in high-quality, relevant images.
    Consider the target audience and content tone when designing image prompts.
    """,
    output_type=ImageDescription,
)

# 5. Publisher Agent
publisher_agent = Agent[None](
    name="Publisher Agent",
    instructions="""You are a publishing agent. Your job is to:
    1. Take all the content components and create a final interactive HTML article
    2. Combine markdown content, images, and metadata into a cohesive publication
    3. Ensure the final output is professional and engaging
    4. Create a responsive, interactive web page
    
    Focus on creating a polished, professional final product that showcases the content effectively.
    """,
    tools=[save_file, create_html_template],
    output_type=PublishedArticle,
)


# ========================= MAIN WORKFLOW =========================


async def create_content_workflow(user_topic: str) -> PublishedArticle:
    """
    Main workflow for the multi-agent content creation system
    """

    with trace("Content Creation Workflow"):
        print("🚀 Starting Multi-Agent Content Creation System")
        print("=" * 60)

        # Step 1: Process User Input
        print("📝 Step 1: Processing user input...")
        user_input_result = await Runner.run(
            user_input_agent, f"Process this topic for content creation: {user_topic}"
        )
        user_input_data = user_input_result.final_output
        print(f"✅ Topic validated: {user_input_data.topic}")

        # Step 2: Research the Topic
        print("\n🔍 Step 2: Researching the topic...")
        research_result = await Runner.run(
            research_agent,
            f"""Research this topic comprehensively:
            Topic: {user_input_data.topic}
            Target Audience: {user_input_data.target_audience}
            Content Length: {user_input_data.content_length}
            Include Technical Details: {user_input_data.include_technical_details}
            
            Provide thorough research with key points, detailed information, sources, and related topics.
            """,
        )
        research_data = research_result.final_output
        print(
            f"✅ Research completed: {len(research_data.key_points)} key points found"
        )

        # Step 3: Convert to Markdown
        print("\n📄 Step 3: Creating structured content...")
        markdown_result = await Runner.run(
            markdown_agent,
            f"""Convert this research into well-structured markdown content:
            
            Topic: {research_data.topic}
            Key Points: {research_data.key_points}
            Detailed Information: {research_data.detailed_information}
            Sources: {research_data.sources}
            Related Topics: {research_data.related_topics}
            
            Target Audience: {user_input_data.target_audience}
            Content Length: {user_input_data.content_length}
            
            Create engaging, well-formatted markdown with proper headers, lists, and formatting.
            """,
        )
        markdown_data = markdown_result.final_output
        print(f"✅ Content structured: {len(markdown_data.sections)} sections created")

        # Step 4: Generate Image Descriptions
        print("\n🎨 Step 4: Creating image descriptions...")
        image_result = await Runner.run(
            image_agent,
            f"""Create detailed image prompts for this content:
            
            Title: {markdown_data.title}
            Summary: {markdown_data.summary}
            Sections: {markdown_data.sections}
            Keywords: {markdown_data.keywords}
            Content: {markdown_data.markdown_content[:500]}...
            
            Create a main hero image and section images that would enhance this content.
            """,
        )
        image_data = image_result.final_output
        print(
            f"✅ Image prompts created: 1 main + {len(image_data.section_images)} section images"
        )

        # Step 5: Publish the Article
        print("\n🌐 Step 5: Publishing the article...")

        # Create image placeholder URLs (in a real implementation, you'd generate actual images)
        image_urls = [
            f"https://via.placeholder.com/600x400/667eea/white?text=Main+Image",
            *[
                f"https://via.placeholder.com/400x300/764ba2/white?text=Section+{i+1}"
                for i in range(len(image_data.section_images))
            ],
        ]

        publish_input = f"""
        Create and publish an interactive HTML article with this content:
        
        Title: {markdown_data.title}
        Content: {markdown_data.markdown_content}
        Image URLs: {image_urls}
        
        Main Image Prompt: {image_data.main_image_prompt}
        Section Images: {image_data.section_images}
        Image Style: {image_data.image_style}
        
        Save the HTML file in the output directory with a descriptive filename.
        """

        publish_result = await Runner.run(publisher_agent, publish_input)
        final_article = publish_result.final_output

        print(f"✅ Article published: {final_article.html_file_path}")
        print(
            f"📊 Stats: {final_article.word_count} words, {final_article.sections_count} sections"
        )

        return final_article


# ========================= CLI INTERFACE =========================


async def main():
    """Main function to run the content creation system"""
    print("🎯 Multi-Agent Content Creation System")
    print("=====================================")
    print()

    # Get user input
    topic = input("📝 Enter the topic you'd like to create content about: ").strip()

    if not topic:
        print("❌ Please provide a valid topic!")
        return

    try:
        # Run the workflow
        result = await create_content_workflow(topic)

        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Content creation completed!")
        print("=" * 60)
        print(f"📄 Article: {result.article_title}")
        print(f"📁 File: {result.html_file_path}")
        print(f"📊 Word count: {result.word_count}")
        print(f"📑 Sections: {result.sections_count}")
        print(f"🖼️  Images: {result.images_included}")
        print(f"📅 Published: {result.publish_date}")
        print()
        print("💡 Open the HTML file in your browser to view the interactive article!")

    except Exception as e:
        print(f"❌ Error during content creation: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
