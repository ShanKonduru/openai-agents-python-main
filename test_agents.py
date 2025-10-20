"""
OpenAI Agents SDK Test Script
This script tests the basic functionality of the OpenAI Agents SDK
"""

import os
import sys
from agents import Agent, Runner

def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OpenAI API key is not set!")
        print()
        print("🔧 How to fix this:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Set it using one of these methods:")
        print()
        print("   Method A - PowerShell:")
        print("   $env:OPENAI_API_KEY = 'your-api-key-here'")
        print()
        print("   Method B - Command Prompt:")
        print("   set OPENAI_API_KEY=your-api-key-here")
        print()
        print("   Method C - Use setup script:")
        print("   Edit and run: .\\006_setup_api_key.ps1")
        print()
        return False
    
    if api_key == "your-openai-api-key-here":
        print("❌ ERROR: Please replace the placeholder with your actual API key!")
        return False
    
    # Mask the key for display
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"✅ OpenAI API key found: {masked_key}")
    return True

def test_basic_agent():
    """Test basic agent functionality"""
    print("\n🧪 Testing basic agent functionality...")
    
    try:
        agent = Agent(
            name="Test Assistant", 
            instructions="You are a helpful assistant that responds very concisely."
        )
        
        print("📝 Running test query...")
        result = Runner.run_sync(agent, "Say 'Hello from OpenAI Agents SDK!' in exactly those words.")
        
        print("✅ Success! Agent response:")
        print(f"   {result.final_output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 OpenAI Agents SDK Test")
    print("=" * 40)
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    # Test basic functionality
    if test_basic_agent():
        print("\n🎉 All tests passed! OpenAI Agents SDK is working correctly.")
    else:
        print("\n💥 Tests failed. Please check your setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()