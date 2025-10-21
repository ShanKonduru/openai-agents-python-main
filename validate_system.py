"""
Comprehensive Validation Test for Download and Preview Functionality
Tests all aspects of the content creation, preview, and download features
"""
import requests
import time
import json
import os
import tempfile
from pathlib import Path

class ContentSystemValidator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.task_id = None
        self.final_result = None
        
    def test_server_health(self):
        """Test if the API server is running and responsive"""
        print("🏥 Testing Server Health...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and responsive")
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server health check failed: {e}")
            return False
    
    def test_content_creation(self):
        """Test content creation endpoint"""
        print("\n📝 Testing Content Creation...")
        
        test_data = {
            "topic": "AI Testing Framework Validation",
            "audience": "Software Engineers",
            "style": "Technical",
            "length": "Short"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/content/create", json=test_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.task_id = data.get("task_id")
                print(f"✅ Content creation started - Task ID: {self.task_id}")
                print(f"📊 Initial status: {data.get('status')}")
                return True
            else:
                print(f"❌ Content creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Content creation error: {e}")
            return False
    
    def wait_for_completion(self, timeout=120):
        """Wait for content creation to complete"""
        print("\n⏳ Waiting for Content Generation...")
        
        if not self.task_id:
            print("❌ No task ID available")
            return False
            
        start_time = time.time()
        last_operation = ""
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/api/content/status/{self.task_id}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    current_op = data.get("current_operation", "")
                    
                    # Only print if operation changed
                    if current_op != last_operation:
                        print(f"📋 {status}: {current_op}")
                        last_operation = current_op
                    
                    if status == "completed":
                        self.final_result = data.get("final_result")
                        print("✅ Content generation completed!")
                        return True
                    elif status == "error":
                        error_msg = data.get("error", "Unknown error")
                        print(f"❌ Content generation failed: {error_msg}")
                        return False
                        
                elif response.status_code == 404:
                    print("❌ Task not found")
                    return False
                    
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                
            time.sleep(3)
            
        print("❌ Timeout waiting for completion")
        return False
    
    def validate_content_structure(self):
        """Validate the structure of generated content"""
        print("\n🔍 Validating Content Structure...")
        
        if not self.final_result:
            print("❌ No final result available")
            return False
            
        required_fields = [
            "title", "content", "markdown_content", "html_content", 
            "article_url_slug", "word_count", "metadata"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in self.final_result:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
            
        print("✅ All required fields present")
        
        # Validate content quality
        markdown_content = self.final_result.get("markdown_content", "")
        html_content = self.final_result.get("html_content", "")
        article_slug = self.final_result.get("article_url_slug", "")
        
        validation_results = {
            "markdown_length": len(markdown_content),
            "html_length": len(html_content),
            "slug_format": bool(article_slug and article_slug.replace("-", "").replace("_", "").isalnum()),
            "markdown_has_headers": "#" in markdown_content,
            "html_has_doctype": "<!DOCTYPE html>" in html_content,
            "html_has_styling": "<style>" in html_content or "font-family" in html_content
        }
        
        print(f"📝 Markdown content: {validation_results['markdown_length']} characters")
        print(f"🌐 HTML content: {validation_results['html_length']} characters")
        print(f"🔗 URL slug: '{article_slug}' - Valid format: {validation_results['slug_format']}")
        print(f"📋 Has headers: {validation_results['markdown_has_headers']}")
        print(f"🎨 HTML has DOCTYPE: {validation_results['html_has_doctype']}")
        print(f"💄 HTML has styling: {validation_results['html_has_styling']}")
        
        # Check for "undefined" values
        undefined_checks = {
            "markdown_undefined": "undefined" in markdown_content.lower(),
            "html_undefined": "undefined" in html_content.lower(),
            "slug_undefined": "undefined" in article_slug.lower()
        }
        
        for check, is_undefined in undefined_checks.items():
            if is_undefined:
                print(f"❌ Found 'undefined' in {check}")
                return False
                
        print("✅ No 'undefined' values found")
        
        # Check minimum content lengths
        if validation_results['markdown_length'] < 100:
            print("❌ Markdown content too short")
            return False
            
        if validation_results['html_length'] < 200:
            print("❌ HTML content too short")
            return False
            
        print("✅ Content structure validation passed")
        return True
    
    def test_preview_functionality(self):
        """Test content preview capabilities"""
        print("\n👁️ Testing Preview Functionality...")
        
        if not self.final_result:
            print("❌ No content available for preview")
            return False
            
        # Test that preview data is accessible
        preview_data = {
            "title": self.final_result.get("title"),
            "content_preview": self.final_result.get("markdown_content", "")[:500],
            "word_count": self.final_result.get("word_count"),
            "metadata": self.final_result.get("metadata")
        }
        
        print(f"📰 Title: {preview_data['title']}")
        print(f"📊 Word count: {preview_data['word_count']}")
        print(f"📝 Content preview (first 100 chars): {preview_data['content_preview'][:100]}...")
        
        # Validate preview has meaningful content
        if not preview_data['title'] or len(preview_data['title']) < 5:
            print("❌ Title is missing or too short")
            return False
            
        if not preview_data['content_preview'] or len(preview_data['content_preview']) < 50:
            print("❌ Content preview is missing or too short")
            return False
            
        print("✅ Preview functionality validated")
        return True
    
    def test_download_endpoints(self):
        """Test download endpoint functionality"""
        print("\n📥 Testing Download Endpoints...")
        
        if not self.task_id:
            print("❌ No task ID available for download testing")
            return False
            
        # Test markdown download
        print("📝 Testing Markdown Download...")
        try:
            md_response = requests.get(f"{self.base_url}/api/content/download/{self.task_id}/markdown", timeout=10)
            
            if md_response.status_code == 200:
                print("✅ Markdown download endpoint accessible")
                
                # Check content type
                content_type = md_response.headers.get('content-type', '')
                print(f"📋 Content-Type: {content_type}")
                
                # Check if it's a file download
                disposition = md_response.headers.get('content-disposition', '')
                print(f"📁 Content-Disposition: {disposition}")
                
                # Check content length
                content_length = len(md_response.content)
                print(f"📊 Content length: {content_length} bytes")
                
                if content_length < 100:
                    print("❌ Downloaded markdown content too short")
                    return False
                    
            else:
                print(f"❌ Markdown download failed: {md_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Markdown download error: {e}")
            return False
        
        # Test HTML download
        print("\n🌐 Testing HTML Download...")
        try:
            html_response = requests.get(f"{self.base_url}/api/content/download/{self.task_id}/html", timeout=10)
            
            if html_response.status_code == 200:
                print("✅ HTML download endpoint accessible")
                
                # Check content type
                content_type = html_response.headers.get('content-type', '')
                print(f"📋 Content-Type: {content_type}")
                
                # Check content length
                content_length = len(html_response.content)
                print(f"📊 Content length: {content_length} bytes")
                
                # Validate HTML structure
                html_content = html_response.text
                html_checks = {
                    "has_doctype": "<!DOCTYPE html>" in html_content,
                    "has_html_tags": "<html" in html_content and "</html>" in html_content,
                    "has_head": "<head>" in html_content and "</head>" in html_content,
                    "has_body": "<body>" in html_content and "</body>" in html_content,
                    "has_styling": "<style>" in html_content or "font-family" in html_content
                }
                
                for check, passed in html_checks.items():
                    status = "✅" if passed else "❌"
                    print(f"{status} HTML {check}: {passed}")
                    
                if not all(html_checks.values()):
                    print("❌ HTML structure validation failed")
                    return False
                    
                if content_length < 200:
                    print("❌ Downloaded HTML content too short")
                    return False
                    
            else:
                print(f"❌ HTML download failed: {html_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ HTML download error: {e}")
            return False
        
        print("✅ Download endpoints validation passed")
        return True
    
    def test_file_download_simulation(self):
        """Simulate actual file downloads like the frontend would do"""
        print("\n💾 Testing File Download Simulation...")
        
        if not self.task_id:
            print("❌ No task ID available")
            return False
            
        # Create temp directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test markdown file download
            try:
                md_response = requests.get(f"{self.base_url}/api/content/download/{self.task_id}/markdown")
                if md_response.status_code == 200:
                    md_file = temp_path / "test_article.md"
                    md_file.write_text(md_response.text, encoding='utf-8')
                    
                    if md_file.exists() and md_file.stat().st_size > 0:
                        print(f"✅ Markdown file created: {md_file.stat().st_size} bytes")
                        
                        # Validate content
                        content = md_file.read_text(encoding='utf-8')
                        if "undefined" in content.lower():
                            print("❌ Markdown file contains 'undefined'")
                            return False
                        
                        print(f"📝 Sample content: {content[:100]}...")
                    else:
                        print("❌ Markdown file not created or empty")
                        return False
                        
            except Exception as e:
                print(f"❌ Markdown file test error: {e}")
                return False
            
            # Test HTML file download
            try:
                html_response = requests.get(f"{self.base_url}/api/content/download/{self.task_id}/html")
                if html_response.status_code == 200:
                    html_file = temp_path / "test_article.html"
                    html_file.write_text(html_response.text, encoding='utf-8')
                    
                    if html_file.exists() and html_file.stat().st_size > 0:
                        print(f"✅ HTML file created: {html_file.stat().st_size} bytes")
                        
                        # Validate content
                        content = html_file.read_text(encoding='utf-8')
                        if "undefined" in content.lower():
                            print("❌ HTML file contains 'undefined'")
                            return False
                        
                        if not content.startswith("<!DOCTYPE html>"):
                            print("❌ HTML file doesn't start with DOCTYPE")
                            return False
                            
                        print(f"🌐 HTML preview: {content[:150]}...")
                    else:
                        print("❌ HTML file not created or empty")
                        return False
                        
            except Exception as e:
                print(f"❌ HTML file test error: {e}")
                return False
        
        print("✅ File download simulation passed")
        return True
    
    def run_complete_validation(self):
        """Run all validation tests"""
        print("🧪 COMPREHENSIVE CONTENT SYSTEM VALIDATION")
        print("=" * 60)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Content Creation", self.test_content_creation),
            ("Content Generation", self.wait_for_completion),
            ("Content Structure", self.validate_content_structure),
            ("Preview Functionality", self.test_preview_functionality),
            ("Download Endpoints", self.test_download_endpoints),
            ("File Download Simulation", self.test_file_download_simulation)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                results[test_name] = result
                
                if result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall Score: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL VALIDATIONS PASSED! System is fully functional.")
            return True
        else:
            print("⚠️ Some validations failed. Please review the issues above.")
            return False

if __name__ == "__main__":
    validator = ContentSystemValidator()
    success = validator.run_complete_validation()
    
    if success:
        print("\n✅ VALIDATION COMPLETE: Preview and Download functionality is working correctly!")
    else:
        print("\n❌ VALIDATION FAILED: Issues found that need to be addressed.")