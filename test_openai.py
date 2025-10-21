"""
Simple test to check OpenAI API connectivity
"""
import openai
from pathlib import Path

# Load API key
key_file = Path("openai_key.txt")
if key_file.exists():
    api_key = key_file.read_text().strip()
    print(f"API Key loaded: {api_key[:20]}...")
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        print("Testing OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=50,
            timeout=10
        )
        print("✅ OpenAI API working!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
else:
    print("❌ API key file not found")