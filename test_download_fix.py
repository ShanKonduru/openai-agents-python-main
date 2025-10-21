"""
Quick test for the fixed download functionality
"""
import requests
import time
import json

def test_content_creation_and_download():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Content Creation and Download Fix...")
    
    # 1. Create content
    print("📝 Creating content...")
    create_data = {
        "topic": "Quick Test Article",
        "audience": "Developers", 
        "style": "Technical",
        "length": "Short"
    }
    
    try:
        response = requests.post(f"{base_url}/api/content/create", json=create_data)
        if response.status_code != 200:
            print(f"❌ Create failed: {response.status_code} {response.text}")
            return False
            
        task_data = response.json()
        task_id = task_data["task_id"]
        print(f"✅ Task created: {task_id}")
        
        # 2. Wait for completion
        print("⏳ Waiting for completion...")
        for i in range(60):  # Wait up to 60 seconds
            status_response = requests.get(f"{base_url}/api/content/status/{task_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 Status: {status_data.get('status')} - {status_data.get('current_operation', '')}")
                
                if status_data.get("status") == "completed":
                    print("✅ Content creation completed!")
                    
                    # Check if we have the required fields
                    final_result = status_data.get("final_result", {})
                    print(f"🔍 Final result fields: {list(final_result.keys())}")
                    
                    # Check specific fields
                    has_markdown = "markdown_content" in final_result
                    has_html = "html_content" in final_result  
                    has_slug = "article_url_slug" in final_result
                    
                    print(f"📝 Has markdown_content: {has_markdown}")
                    print(f"🌐 Has html_content: {has_html}")
                    print(f"🔗 Has article_url_slug: {has_slug}")
                    
                    if has_markdown and has_html and has_slug:
                        print("✅ All required fields present!")
                        
                        # Test content preview
                        markdown_content = final_result.get("markdown_content", "")
                        html_content = final_result.get("html_content", "")
                        
                        print(f"📝 Markdown length: {len(markdown_content)} chars")
                        print(f"🌐 HTML length: {len(html_content)} chars")
                        
                        if markdown_content and markdown_content != "undefined":
                            print("✅ Markdown content looks good!")
                        else:
                            print("❌ Markdown content is undefined or empty")
                            
                        if html_content and html_content != "undefined":
                            print("✅ HTML content looks good!")
                        else:
                            print("❌ HTML content is undefined or empty")
                            
                        return True
                    else:
                        print("❌ Missing required fields for download")
                        return False
                        
                elif status_data.get("status") == "error":
                    print(f"❌ Error: {status_data.get('error')}")
                    return False
                    
            time.sleep(2)
            
        print("❌ Timed out waiting for completion")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_content_creation_and_download()
    if success:
        print("\n🎉 Download fix test PASSED! The undefined issue should be resolved.")
    else:
        print("\n💥 Download fix test FAILED. There may still be issues.")