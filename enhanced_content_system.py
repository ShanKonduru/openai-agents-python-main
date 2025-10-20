"""
Advanced Multi-Agent Content Creation System
===========================================

Enhanced version with actual image generation and better workflow management.
"""

import asyncio
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from agents import Agent, Runner, function_tool, trace
from pydantic import BaseModel, Field


# ========================= ENHANCED DATA MODELS =========================

class ContentCreationConfig(BaseModel):
    """Configuration for the content creation process"""
    output_directory: str = "output"
    generate_real_images: bool = False  # Set to True if you have image generation setup
    max_word_count: int = 2000
    include_toc: bool = True
    include_references: bool = True


class UserInput(BaseModel):
    """Enhanced user input validation model"""
    topic: str = Field(description="The topic to research and create content about")
    target_audience: str = Field(default="general", description="Target audience for the content")
    content_type: str = Field(default="article", description="Type of content: article, tutorial, guide, analysis")
    content_length: str = Field(default="medium", description="Desired content length: short, medium, long")
    include_technical_details: bool = Field(default=False, description="Whether to include technical details")
    tone: str = Field(default="professional", description="Content tone: professional, casual, academic, friendly")


class ResearchOutput(BaseModel):
    """Enhanced research agent output model"""
    topic: str
    executive_summary: str = Field(description="Brief executive summary of the research")
    key_points: List[str] = Field(description="Key points discovered during research")
    detailed_sections: Dict[str, str] = Field(description="Detailed information organized by sections")
    statistics: List[str] = Field(description="Relevant statistics and data points")
    expert_quotes: List[str] = Field(description="Expert opinions or notable quotes")
    sources: List[str] = Field(description="Research sources and references")
    related_topics: List[str] = Field(description="Related topics for further exploration")
    research_quality_score: int = Field(description="Self-assessed quality score 1-10")


class MarkdownContent(BaseModel):
    """Enhanced markdown agent output model"""
    title: str = Field(description="Article title")
    subtitle: str = Field(description="Article subtitle")
    summary: str = Field(description="Brief summary of the content")
    table_of_contents: List[str] = Field(description="Table of contents entries")
    markdown_content: str = Field(description="Full markdown formatted content")
    sections: List[str] = Field(description="List of main sections")
    keywords: List[str] = Field(description="Important keywords for SEO")
    meta_description: str = Field(description="SEO meta description")
    estimated_read_time: str = Field(description="Estimated reading time")


class ImageDescription(BaseModel):
    """Enhanced image generation description model"""
    hero_image: Dict[str, str] = Field(description="Main hero image with prompt and alt text")
    section_images: List[Dict[str, str]] = Field(description="Section images with prompts and alt text")
    image_style: str = Field(description="Style guide for images")
    color_scheme: str = Field(description="Recommended color scheme")
    aspect_ratios: Dict[str, str] = Field(description="Recommended aspect ratios for different images")


class PublishedArticle(BaseModel):
    """Enhanced final published article model"""
    html_file_path: str = Field(description="Path to the generated HTML file")
    markdown_file_path: str = Field(description="Path to the markdown source file")
    article_title: str
    article_url_slug: str = Field(description="URL-friendly slug")
    word_count: int
    sections_count: int
    images_included: int
    publish_date: str
    estimated_read_time: str
    seo_score: int = Field(description="SEO optimization score 1-10")


# ========================= ENHANCED UTILITY FUNCTIONS =========================

@function_tool
def create_url_slug(title: str) -> str:
    """Create a URL-friendly slug from a title"""
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug


@function_tool
def calculate_read_time(content: str) -> str:
    """Calculate estimated reading time based on word count"""
    word_count = len(content.split())
    # Average reading speed: 200-250 words per minute
    minutes = max(1, round(word_count / 225))
    return f"{minutes} min read"


@function_tool
def save_markdown_file(content: str, title: str, directory: str = "output") -> str:
    """Save markdown content to file"""
    output_dir = Path(directory)
    output_dir.mkdir(exist_ok=True)
    
    slug = create_url_slug(title)
    filename = f"{slug}.md"
    file_path = output_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(file_path.absolute())


@function_tool
def create_enhanced_html_template(
    title: str, 
    subtitle: str,
    content: str, 
    toc: List[str] = None,
    meta_description: str = "",
    read_time: str = "5 min read",
    image_urls: List[str] = None
) -> str:
    """Create an enhanced interactive HTML template"""
    if image_urls is None:
        image_urls = []
    if toc is None:
        toc = []
    
    # Generate TOC HTML
    toc_html = ""
    if toc:
        toc_html = """
        <div class="table-of-contents">
            <h3>📋 Table of Contents</h3>
            <ul>
        """
        for item in toc:
            anchor = create_url_slug(item)
            toc_html += f'<li><a href="#{anchor}">{item}</a></li>'
        toc_html += """
            </ul>
        </div>
        """
    
    # Hero image
    hero_image_html = ""
    if image_urls:
        hero_image_html = f"""
        <div class="hero-image">
            <img src="{image_urls[0]}" alt="Hero image for {title}" />
        </div>
        """
    
    # Image gallery for additional images
    gallery_html = ""
    if len(image_urls) > 1:
        gallery_html = """
        <div class="image-gallery">
            <h3>📸 Related Images</h3>
            <div class="gallery-grid">
        """
        for i, url in enumerate(image_urls[1:], 1):
            gallery_html += f"""
                <div class="gallery-item">
                    <img src="{url}" alt="Article Image {i}" onclick="openModal(this)" loading="lazy">
                </div>
            """
        gallery_html += """
            </div>
        </div>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="{meta_description}">
        <meta name="keywords" content="content creation, AI agents, research, article">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{meta_description}">
        <meta property="og:type" content="article">
        <title>{title}</title>
        
        <!-- Enhanced Styles -->
        <style>
            :root {{
                --primary-color: #667eea;
                --secondary-color: #764ba2;
                --accent-color: #f093fb;
                --text-color: #2c3e50;
                --text-light: #7f8c8d;
                --background-light: #f8f9fa;
                --border-color: #e9ecef;
                --success-color: #27ae60;
                --warning-color: #f39c12;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.7;
                color: var(--text-color);
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 900px;
                margin: 20px auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0,0,0,0.15);
                overflow: hidden;
                animation: fadeIn 0.8s ease-out;
            }}
            
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(30px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .header {{
                background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 50px 40px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
                background-size: 20px 20px;
                animation: float 20s linear infinite;
            }}
            
            @keyframes float {{
                0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
                100% {{ transform: translate(-50%, -50%) rotate(360deg); }}
            }}
            
            .header h1 {{
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                position: relative;
                z-index: 1;
            }}
            
            .header .subtitle {{
                font-size: 1.3em;
                opacity: 0.9;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
            }}
            
            .header .meta-info {{
                display: flex;
                justify-content: center;
                gap: 30px;
                flex-wrap: wrap;
                position: relative;
                z-index: 1;
            }}
            
            .meta-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 1.1em;
            }}
            
            .hero-image {{
                width: 100%;
                height: 300px;
                overflow: hidden;
            }}
            
            .hero-image img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.5s ease;
            }}
            
            .hero-image img:hover {{
                transform: scale(1.05);
            }}
            
            .content {{
                padding: 50px 40px;
            }}
            
            .table-of-contents {{
                background: var(--background-light);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 40px;
                border-left: 5px solid var(--primary-color);
            }}
            
            .table-of-contents h3 {{
                color: var(--text-color);
                margin-bottom: 15px;
                font-size: 1.3em;
            }}
            
            .table-of-contents ul {{
                list-style: none;
            }}
            
            .table-of-contents li {{
                margin-bottom: 8px;
            }}
            
            .table-of-contents a {{
                color: var(--primary-color);
                text-decoration: none;
                padding: 5px 10px;
                border-radius: 5px;
                transition: all 0.3s ease;
                display: block;
            }}
            
            .table-of-contents a:hover {{
                background: var(--primary-color);
                color: white;
                transform: translateX(10px);
            }}
            
            .content h1, .content h2, .content h3 {{
                color: var(--text-color);
                margin-top: 40px;
                margin-bottom: 20px;
                scroll-margin-top: 20px;
            }}
            
            .content h1 {{
                font-size: 2.2em;
                border-bottom: 3px solid var(--primary-color);
                padding-bottom: 15px;
                margin-bottom: 25px;
            }}
            
            .content h2 {{
                font-size: 1.8em;
                color: var(--secondary-color);
                position: relative;
            }}
            
            .content h2::before {{
                content: '▶';
                color: var(--primary-color);
                margin-right: 10px;
            }}
            
            .content h3 {{
                font-size: 1.4em;
                color: var(--text-light);
            }}
            
            .content p {{
                margin-bottom: 25px;
                text-align: justify;
                font-size: 1.1em;
                line-height: 1.8;
            }}
            
            .content ul, .content ol {{
                margin: 20px 0 25px 30px;
            }}
            
            .content li {{
                margin-bottom: 10px;
                font-size: 1.05em;
                line-height: 1.6;
            }}
            
            .content blockquote {{
                border-left: 5px solid var(--accent-color);
                padding: 20px 25px;
                margin: 30px 0;
                background: linear-gradient(90deg, var(--background-light), white);
                border-radius: 0 10px 10px 0;
                font-style: italic;
                position: relative;
            }}
            
            .content blockquote::before {{
                content: '"';
                font-size: 3em;
                color: var(--accent-color);
                position: absolute;
                top: -10px;
                left: 10px;
            }}
            
            .content code {{
                background: var(--background-light);
                padding: 4px 8px;
                border-radius: 5px;
                font-family: 'Fira Code', 'Courier New', monospace;
                font-size: 0.9em;
                color: var(--secondary-color);
            }}
            
            .content pre {{
                background: var(--text-color);
                color: white;
                padding: 25px;
                border-radius: 10px;
                overflow-x: auto;
                margin: 30px 0;
                position: relative;
            }}
            
            .content pre::before {{
                content: '';
                position: absolute;
                top: 15px;
                left: 15px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #ff5f56;
                box-shadow: 20px 0 #ffbd2e, 40px 0 #27ca3f;
            }}
            
            .image-gallery {{
                margin-top: 50px;
                padding-top: 40px;
                border-top: 2px solid var(--border-color);
            }}
            
            .gallery-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
                margin-top: 25px;
            }}
            
            .gallery-item {{
                position: relative;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }}
            
            .gallery-item:hover {{
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }}
            
            .gallery-item img {{
                width: 100%;
                height: 200px;
                object-fit: cover;
                cursor: pointer;
                transition: transform 0.3s ease;
            }}
            
            .gallery-item:hover img {{
                transform: scale(1.1);
            }}
            
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.95);
                animation: modalFadeIn 0.3s ease-out;
            }}
            
            @keyframes modalFadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            
            .modal-content {{
                margin: auto;
                display: block;
                width: 90%;
                max-width: 800px;
                max-height: 90%;
                margin-top: 2%;
                border-radius: 10px;
                animation: modalSlideIn 0.3s ease-out;
            }}
            
            @keyframes modalSlideIn {{
                from {{ transform: translateY(-50px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}
            
            .close {{
                position: absolute;
                top: 20px;
                right: 40px;
                color: white;
                font-size: 50px;
                font-weight: bold;
                cursor: pointer;
                transition: color 0.3s ease;
                z-index: 1001;
            }}
            
            .close:hover {{
                color: var(--accent-color);
            }}
            
            .footer {{
                background: var(--text-color);
                color: white;
                text-align: center;
                padding: 30px;
                font-size: 1em;
            }}
            
            .footer a {{
                color: var(--accent-color);
                text-decoration: none;
            }}
            
            .progress-bar {{
                position: fixed;
                top: 0;
                left: 0;
                width: 0%;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
                z-index: 1000;
                transition: width 0.3s ease;
            }}
            
            /* Responsive Design */
            @media (max-width: 768px) {{
                .container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                
                .header {{
                    padding: 40px 25px;
                }}
                
                .header h1 {{
                    font-size: 2.2em;
                }}
                
                .header .meta-info {{
                    gap: 15px;
                }}
                
                .content {{
                    padding: 40px 25px;
                }}
                
                .gallery-grid {{
                    grid-template-columns: 1fr;
                    gap: 20px;
                }}
                
                .table-of-contents {{
                    padding: 20px;
                }}
            }}
            
            /* Print Styles */
            @media print {{
                .header, .footer, .modal, .progress-bar {{
                    display: none !important;
                }}
                
                .container {{
                    box-shadow: none;
                    border-radius: 0;
                    margin: 0;
                }}
                
                .content {{
                    padding: 0;
                }}
                
                .gallery-item img {{
                    max-height: 200px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="progress-bar" id="progressBar"></div>
        
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                <div class="subtitle">{subtitle}</div>
                <div class="meta-info">
                    <div class="meta-item">
                        <span>📅</span>
                        <span>{datetime.now().strftime('%B %d, %Y')}</span>
                    </div>
                    <div class="meta-item">
                        <span>⏱️</span>
                        <span>{read_time}</span>
                    </div>
                    <div class="meta-item">
                        <span>🤖</span>
                        <span>AI Generated</span>
                    </div>
                </div>
            </div>
            
            {hero_image_html}
            
            <div class="content">
                {toc_html}
                {content}
                {gallery_html}
            </div>
            
            <div class="footer">
                <p>Generated by <strong>Multi-Agent Content Creation System</strong></p>
                <p>Powered by <a href="https://github.com/openai/openai-agents-python" target="_blank">OpenAI Agents SDK</a></p>
            </div>
        </div>
        
        <!-- Modal for image viewing -->
        <div id="imageModal" class="modal">
            <span class="close" onclick="closeModal()">&times;</span>
            <img class="modal-content" id="modalImage">
        </div>
        
        <script>
            // Progress bar functionality
            function updateProgressBar() {{
                const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
                const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrollPercent = (scrollTop / scrollHeight) * 100;
                document.getElementById('progressBar').style.width = scrollPercent + '%';
            }}
            
            window.addEventListener('scroll', updateProgressBar);
            
            // Modal functionality
            function openModal(img) {{
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                modal.style.display = 'block';
                modalImg.src = img.src;
                document.body.style.overflow = 'hidden';
            }}
            
            function closeModal() {{
                document.getElementById('imageModal').style.display = 'none';
                document.body.style.overflow = 'auto';
            }}
            
            // Close modal when clicking outside the image
            document.getElementById('imageModal').onclick = function(event) {{
                if (event.target === this) {{
                    closeModal();
                }}
            }}
            
            // Keyboard navigation
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape') {{
                    closeModal();
                }}
            }});
            
            // Smooth scrolling for TOC links
            document.querySelectorAll('.table-of-contents a').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ behavior: 'smooth' }});
                    }}
                }});
            }});
            
            // Add copy to clipboard for code blocks
            document.querySelectorAll('pre').forEach(pre => {{
                const copyButton = document.createElement('button');
                copyButton.textContent = 'Copy';
                copyButton.style.cssText = 'position: absolute; top: 10px; right: 10px; background: var(--accent-color); color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px;';
                pre.style.position = 'relative';
                pre.appendChild(copyButton);
                
                copyButton.addEventListener('click', () => {{
                    navigator.clipboard.writeText(pre.textContent).then(() => {{
                        copyButton.textContent = 'Copied!';
                        setTimeout(() => copyButton.textContent = 'Copy', 2000);
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html_template


# ========================= ENHANCED AGENT DEFINITIONS =========================

# 1. Enhanced User Input Agent
user_input_agent = Agent[None](
    name="User Input Agent",
    instructions="""You are an advanced user input validation and enhancement agent. Your responsibilities:

    1. VALIDATE input thoroughly:
       - Ensure the topic is specific enough for quality content creation
       - Check if the topic is appropriate and not harmful
       - Verify the topic has sufficient scope for meaningful content

    2. ENHANCE input by:
       - Suggesting improvements to vague topics
       - Recommending appropriate target audiences
       - Determining optimal content type and tone

    3. GUIDE users by:
       - Asking clarifying questions when needed
       - Providing examples of better topic formulations
       - Explaining why certain parameters are recommended

    Be helpful, professional, and ensure the final output will lead to high-quality content creation.
    """,
    output_type=UserInput,
)

# 2. Enhanced Research Agent
research_agent = Agent[None](
    name="Research Agent",
    instructions="""You are a comprehensive research specialist. Your mission:

    1. CONDUCT thorough research:
       - Gather current, accurate information from multiple perspectives
       - Include relevant statistics, data points, and trends
       - Find expert opinions and authoritative quotes
       - Identify both common knowledge and unique insights

    2. ORGANIZE findings systematically:
       - Create clear sections for different aspects of the topic
       - Prioritize information by relevance and credibility
       - Maintain factual accuracy and cite conceptual sources

    3. EVALUATE research quality:
       - Assess the comprehensiveness of your findings
       - Identify any gaps that need additional research
       - Rate your own research quality honestly

    Focus on providing comprehensive, well-structured research that serves as an excellent foundation for content creation.
    """,
    output_type=ResearchOutput,
)

# 3. Enhanced Markdown Agent
markdown_agent = Agent[None](
    name="Content Structuring Agent",
    instructions="""You are a content architecture and writing specialist. Your role:

    1. STRUCTURE content expertly:
       - Create compelling titles and subtitles
       - Develop logical content flow with clear sections
       - Build comprehensive table of contents
       - Ensure proper information hierarchy

    2. WRITE engaging content:
       - Transform research into readable, flowing prose
       - Match the specified tone and target audience
       - Use appropriate markdown formatting for emphasis
       - Include relevant examples and practical applications

    3. OPTIMIZE for engagement:
       - Create SEO-friendly elements (titles, descriptions, keywords)
       - Calculate accurate reading time estimates
       - Ensure content length matches requirements
       - Add compelling quotes and callouts where appropriate

    Produce content that is informative, engaging, and professionally structured.
    """,
    output_type=MarkdownContent,
)

# 4. Enhanced Image Agent
image_agent = Agent[None](
    name="Visual Content Designer",
    instructions="""You are a visual content strategy expert. Your focus:

    1. DESIGN visual narrative:
       - Create a compelling hero image that captures the essence
       - Design section images that support and enhance the content
       - Ensure visual consistency and brand coherence
       - Consider the target audience's visual preferences

    2. CRAFT detailed prompts:
       - Write specific, detailed image generation prompts
       - Include style, composition, color, and mood specifications
       - Specify appropriate aspect ratios for different uses
       - Consider technical requirements for web display

    3. ENHANCE accessibility:
       - Provide meaningful alt text for all images
       - Consider color contrast and readability
       - Ensure images add value, not just decoration

    Create visual content strategies that truly enhance the reader's experience and understanding.
    """,
    output_type=ImageDescription,
)

# 5. Enhanced Publisher Agent
publisher_agent = Agent[None](
    name="Digital Publishing Specialist",
    instructions="""You are a digital publishing expert responsible for final content assembly. Your duties:

    1. ASSEMBLE content professionally:
       - Combine all content elements into a cohesive publication
       - Ensure proper formatting and visual hierarchy
       - Create responsive, accessible web pages
       - Maintain consistent branding and design

    2. OPTIMIZE for web:
       - Generate SEO-friendly URLs and metadata
       - Ensure fast loading and mobile responsiveness
       - Include proper meta tags and social sharing elements
       - Create user-friendly navigation and interactions

    3. QUALITY ASSURANCE:
       - Review final output for errors and improvements
       - Ensure all links and interactions work properly
       - Validate HTML structure and accessibility
       - Rate the overall publication quality

    Deliver a polished, professional publication that showcases the content effectively.
    """,
    tools=[save_markdown_file, create_enhanced_html_template, create_url_slug, calculate_read_time],
    output_type=PublishedArticle,
)


# ========================= ENHANCED WORKFLOW =========================

async def create_enhanced_content_workflow(
    user_topic: str, 
    config: ContentCreationConfig = ContentCreationConfig()
) -> PublishedArticle:
    """
    Enhanced workflow for the multi-agent content creation system
    """
    
    with trace("Enhanced Content Creation Workflow"):
        print("🚀 Starting Enhanced Multi-Agent Content Creation System")
        print("=" * 70)
        
        # Create output directory
        output_dir = Path(config.output_directory)
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Step 1: Process and Enhance User Input
            print("📝 Step 1: Processing and enhancing user input...")
            user_input_result = await Runner.run(
                user_input_agent,
                f"""Analyze and enhance this topic for content creation: "{user_topic}"
                
                Ensure the topic is specific, appropriate, and suitable for creating quality content.
                Recommend appropriate settings for target audience, content type, and tone.
                If the topic needs improvement, suggest enhancements while maintaining the user's intent.
                """
            )
            user_input_data = user_input_result.final_output
            print(f"✅ Topic processed: {user_input_data.topic}")
            print(f"   Audience: {user_input_data.target_audience} | Type: {user_input_data.content_type}")
            
            # Step 2: Comprehensive Research
            print(f"\n🔍 Step 2: Conducting comprehensive research...")
            research_result = await Runner.run(
                research_agent,
                f"""Conduct thorough research on this topic:

                Topic: {user_input_data.topic}
                Content Type: {user_input_data.content_type}
                Target Audience: {user_input_data.target_audience}
                Technical Details: {user_input_data.include_technical_details}
                
                Provide comprehensive research including:
                - Executive summary
                - Key points and detailed sections
                - Relevant statistics and expert quotes
                - Credible sources and references
                - Related topics for context
                
                Aim for a research quality score of 8+ out of 10.
                """
            )
            research_data = research_result.final_output
            print(f"✅ Research completed: Quality score {research_data.research_quality_score}/10")
            print(f"   Sections: {len(research_data.detailed_sections)} | Sources: {len(research_data.sources)}")
            
            # Step 3: Create Structured Content
            print(f"\n📄 Step 3: Creating structured content...")
            markdown_result = await Runner.run(
                markdown_agent,
                f"""Create comprehensive, well-structured content from this research:

                RESEARCH DATA:
                Topic: {research_data.topic}
                Executive Summary: {research_data.executive_summary}
                Key Points: {research_data.key_points}
                Detailed Sections: {research_data.detailed_sections}
                Statistics: {research_data.statistics}
                Expert Quotes: {research_data.expert_quotes}
                Sources: {research_data.sources}

                CONTENT REQUIREMENTS:
                Target Audience: {user_input_data.target_audience}
                Content Type: {user_input_data.content_type}
                Content Length: {user_input_data.content_length}
                Tone: {user_input_data.tone}
                Max Word Count: {config.max_word_count}
                Include TOC: {config.include_toc}
                Include References: {config.include_references}

                Create engaging, well-formatted markdown with:
                - Compelling title and subtitle
                - Comprehensive table of contents
                - Well-structured sections with proper headers
                - SEO-optimized metadata
                - Accurate reading time estimate
                """
            )
            markdown_data = markdown_result.final_output
            print(f"✅ Content structured: {len(markdown_data.sections)} sections")
            print(f"   Reading time: {markdown_data.estimated_read_time} | Keywords: {len(markdown_data.keywords)}")
            
            # Step 4: Design Visual Content Strategy
            print(f"\n🎨 Step 4: Designing visual content strategy...")
            image_result = await Runner.run(
                image_agent,
                f"""Design a comprehensive visual content strategy for this article:

                ARTICLE DETAILS:
                Title: {markdown_data.title}
                Subtitle: {markdown_data.subtitle}
                Summary: {markdown_data.summary}
                Sections: {markdown_data.sections}
                Keywords: {markdown_data.keywords}
                Content Type: {user_input_data.content_type}
                Target Audience: {user_input_data.target_audience}

                CONTENT PREVIEW:
                {markdown_data.markdown_content[:800]}...

                Create detailed image specifications including:
                - Hero image with specific prompt and alt text
                - Section images that enhance understanding
                - Consistent visual style and color scheme
                - Appropriate aspect ratios for web display
                - Professional, engaging visual narrative
                """
            )
            image_data = image_result.final_output
            print(f"✅ Visual strategy created: 1 hero + {len(image_data.section_images)} section images")
            print(f"   Style: {image_data.image_style} | Colors: {image_data.color_scheme}")
            
            # Step 5: Publish the Enhanced Article
            print(f"\n🌐 Step 5: Publishing the enhanced article...")
            
            # Generate placeholder image URLs (replace with actual image generation if available)
            image_urls = []
            if config.generate_real_images:
                # Here you would integrate with actual image generation services
                # For now, we'll use enhanced placeholders
                image_urls = [
                    f"https://picsum.photos/800/400?random={hash(markdown_data.title) % 1000}",
                    *[f"https://picsum.photos/600/300?random={hash(section) % 1000}" 
                      for section in markdown_data.sections[:3]]
                ]
            else:
                image_urls = [
                    f"https://via.placeholder.com/800x400/667eea/white?text=Hero+Image",
                    *[f"https://via.placeholder.com/600x300/764ba2/white?text=Section+{i+1}" 
                      for i in range(min(3, len(image_data.section_images)))]
                ]
            
            # Save markdown file first
            markdown_path = save_markdown_file(
                markdown_data.markdown_content, 
                markdown_data.title, 
                config.output_directory
            )
            
            publish_input = f"""
            Create and publish a professional, interactive HTML article with these specifications:

            CONTENT:
            Title: {markdown_data.title}
            Subtitle: {markdown_data.subtitle}
            Meta Description: {markdown_data.meta_description}
            Table of Contents: {markdown_data.table_of_contents}
            Content: {markdown_data.markdown_content}
            Reading Time: {markdown_data.estimated_read_time}

            VISUALS:
            Image URLs: {image_urls}
            Hero Image: {image_data.hero_image}
            Section Images: {image_data.section_images}
            Visual Style: {image_data.image_style}

            REQUIREMENTS:
            - Create responsive, accessible HTML
            - Include proper SEO metadata
            - Generate URL-friendly slug
            - Save in directory: {config.output_directory}
            - Ensure professional presentation
            - Rate the final SEO optimization (1-10)

            Markdown file saved at: {markdown_path}
            """
            
            publish_result = await Runner.run(publisher_agent, publish_input)
            final_article = publish_result.final_output
            
            print(f"✅ Article published successfully!")
            print(f"   HTML: {final_article.html_file_path}")
            print(f"   Markdown: {final_article.markdown_file_path}")
            print(f"   SEO Score: {final_article.seo_score}/10")
            
            return final_article
            
        except Exception as e:
            print(f"❌ Error during content creation: {e}")
            raise


# ========================= ENHANCED CLI INTERFACE =========================

async def main():
    """Enhanced main function with configuration options"""
    print("🎯 Enhanced Multi-Agent Content Creation System")
    print("=" * 50)
    print("Create professional articles with AI agents!")
    print()
    
    # Get user input
    topic = input("📝 Enter your topic: ").strip()
    
    if not topic:
        print("❌ Please provide a valid topic!")
        return
    
    # Configuration options
    print("\n⚙️  Configuration Options:")
    generate_images = input("🖼️  Generate real images? (y/N): ").lower().startswith('y')
    output_dir = input("📁 Output directory (default: output): ").strip() or "output"
    
    config = ContentCreationConfig(
        output_directory=output_dir,
        generate_real_images=generate_images,
        max_word_count=2000,
        include_toc=True,
        include_references=True
    )
    
    print(f"\n🚀 Starting content creation for: '{topic}'")
    print("-" * 50)
    
    try:
        # Run the enhanced workflow
        result = await create_enhanced_content_workflow(topic, config)
        
        print("\n" + "=" * 70)
        print("🎉 SUCCESS! Enhanced content creation completed!")
        print("=" * 70)
        print(f"📄 Title: {result.article_title}")
        print(f"🔗 Slug: {result.article_url_slug}")
        print(f"📁 HTML File: {result.html_file_path}")
        print(f"📄 Markdown: {result.markdown_file_path}")
        print(f"📊 Stats:")
        print(f"   • Word count: {result.word_count}")
        print(f"   • Sections: {result.sections_count}")
        print(f"   • Images: {result.images_included}")
        print(f"   • Reading time: {result.estimated_read_time}")
        print(f"   • SEO score: {result.seo_score}/10")
        print(f"📅 Published: {result.publish_date}")
        print()
        print("💡 Open the HTML file in your browser to view the interactive article!")
        print(f"   File location: {Path(result.html_file_path).absolute()}")
        
    except Exception as e:
        print(f"❌ Error during content creation: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("• Ensure your OpenAI API key is set correctly")
        print("• Check your internet connection")
        print("• Try a more specific topic")
        print("• Verify the output directory is writable")
        raise


if __name__ == "__main__":
    asyncio.run(main())