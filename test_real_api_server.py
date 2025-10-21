"""
Unit Tests for Content Creation API
Tests the real_api_server.py endpoints and functionality
"""

import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from pathlib import Path

# Import our API server
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('real_api_server.openai') as mock_openai:
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Mock chat completions
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response from OpenAI"
        mock_client.chat.completions.create.return_value = mock_response
        
        yield mock_client

@pytest.fixture
def test_client():
    """Create test client for the API"""
    from real_api_server import app
    return TestClient(app)

@pytest.fixture
def sample_user_input():
    """Sample input for testing"""
    return {
        "topic": "Artificial Intelligence in Healthcare",
        "audience": "Healthcare professionals",
        "style": "Professional",
        "length": "Medium"
    }

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, test_client):
        """Test the health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestContentCreation:
    """Test content creation endpoints"""
    
    def test_create_content_endpoint_structure(self, test_client, sample_user_input):
        """Test content creation endpoint returns proper structure"""
        response = test_client.post("/api/content/create", json=sample_user_input)
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "processing"
    
    def test_create_content_validation(self, test_client):
        """Test input validation for content creation"""
        # Test missing topic
        response = test_client.post("/api/content/create", json={})
        assert response.status_code == 422
        
        # Test empty topic
        response = test_client.post("/api/content/create", json={"topic": ""})
        assert response.status_code == 422
    
    def test_status_endpoint_invalid_task(self, test_client):
        """Test status endpoint with invalid task ID"""
        response = test_client.get("/api/content/status/invalid-task-id")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

class TestContentWorkflow:
    """Test the 5-step content creation workflow"""
    
    @patch('real_api_server.openai')
    def test_step1_research(self, mock_openai, test_client):
        """Test Step 1: Research execution"""
        # Mock OpenAI response for research
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        research_response = Mock()
        research_response.choices = [Mock()]
        research_response.choices[0].message.content = json.dumps({
            "key_points": ["Point 1", "Point 2"],
            "statistics": ["Stat 1", "Stat 2"],
            "expert_insights": ["Insight 1", "Insight 2"],
            "current_trends": ["Trend 1", "Trend 2"]
        })
        mock_client.chat.completions.create.return_value = research_response
        
        # Import and test the research function
        from real_api_server import execute_step1_research
        
        result = execute_step1_research(
            "AI in Healthcare", 
            "Healthcare professionals", 
            "Professional"
        )
        
        assert result is not None
        assert "key_points" in result or isinstance(result, str)
    
    @patch('real_api_server.openai')
    def test_step2_structure(self, mock_openai):
        """Test Step 2: Structure creation"""
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        structure_response = Mock()
        structure_response.choices = [Mock()]
        structure_response.choices[0].message.content = json.dumps({
            "title": "Test Article Title",
            "introduction": "Test introduction",
            "main_sections": ["Section 1", "Section 2"],
            "conclusion": "Test conclusion"
        })
        mock_client.chat.completions.create.return_value = structure_response
        
        from real_api_server import execute_step2_structure
        
        research_data = {"key_points": ["Point 1"], "statistics": ["Stat 1"]}
        result = execute_step2_structure(
            research_data,
            "AI in Healthcare",
            "Medium",
            "Professional"
        )
        
        assert result is not None
    
    @patch('real_api_server.openai')
    def test_step3_content(self, mock_openai):
        """Test Step 3: Content generation"""
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        content_response = Mock()
        content_response.choices = [Mock()]
        content_response.choices[0].message.content = "# Test Article\n\nThis is test content for the article."
        mock_client.chat.completions.create.return_value = content_response
        
        from real_api_server import execute_step3_content
        
        structure_data = {
            "title": "Test Title",
            "introduction": "Test intro",
            "main_sections": ["Section 1"],
            "conclusion": "Test conclusion"
        }
        research_data = {"key_points": ["Point 1"]}
        
        result = execute_step3_content(structure_data, research_data, "Professional")
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

class TestAPIIntegration:
    """Test API integration with OpenAI"""
    
    def test_openai_api_key_loading(self):
        """Test OpenAI API key is loaded correctly"""
        from real_api_server import get_openai_api_key
        
        # Test with environment variable
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            key = get_openai_api_key()
            assert key == 'test-key'
        
        # Test with file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('file-test-key')
            temp_file = f.name
        
        try:
            with patch('real_api_server.Path') as mock_path:
                mock_path.return_value.exists.return_value = True
                mock_path.return_value.read_text.return_value = 'file-test-key'
                key = get_openai_api_key()
                # This will fall back to environment or file
                assert key is not None
        finally:
            os.unlink(temp_file)

class TestFileOperations:
    """Test file download and generation operations"""
    
    def test_markdown_download(self, test_client):
        """Test markdown file download"""
        # First create some content
        with patch('real_api_server.task_storage') as mock_storage:
            mock_storage.get.return_value = {
                'status': 'completed',
                'final_result': {
                    'content': '# Test Article\n\nThis is test content.'
                }
            }
            
            response = test_client.get("/api/content/download/test-task/markdown")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/octet-stream"
    
    def test_html_download(self, test_client):
        """Test HTML file download"""
        with patch('real_api_server.task_storage') as mock_storage:
            mock_storage.get.return_value = {
                'status': 'completed',
                'final_result': {
                    'content': '# Test Article\n\nThis is test content.'
                }
            }
            
            response = test_client.get("/api/content/download/test-task/html")
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/octet-stream"

class TestErrorHandling:
    """Test error handling scenarios"""
    
    @patch('real_api_server.openai')
    def test_openai_api_error(self, mock_openai, test_client, sample_user_input):
        """Test handling of OpenAI API errors"""
        mock_client = Mock()
        mock_openai.OpenAI.return_value = mock_client
        
        # Mock API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        response = test_client.post("/api/content/create", json=sample_user_input)
        assert response.status_code == 200  # Should still return task ID
        
        # Check if error is properly handled in status
        data = response.json()
        task_id = data["task_id"]
        
        # Wait a moment for processing
        import time
        time.sleep(2)
        
        status_response = test_client.get(f"/api/content/status/{task_id}")
        # Should either be processing or have error status
        assert status_response.status_code in [200, 404]

class TestConcurrency:
    """Test concurrent request handling"""
    
    def test_multiple_requests(self, test_client, sample_user_input):
        """Test handling multiple concurrent requests"""
        responses = []
        
        # Send multiple requests
        for i in range(3):
            input_data = sample_user_input.copy()
            input_data["topic"] = f"Topic {i+1}"
            response = test_client.post("/api/content/create", json=input_data)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
        
        # All task IDs should be unique
        task_ids = [response.json()["task_id"] for response in responses]
        assert len(set(task_ids)) == len(task_ids)

# Test configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])