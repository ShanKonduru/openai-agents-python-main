import os
import sys
from dotenv import load_dotenv

from agents import Agent, Runner

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check if OpenAI API key is set
if not OPENAI_API_KEY:
    print("❌ ERROR: OpenAI API key is not set!")
    print()
    print("🔧 Please set your OpenAI API key:")
    print("PowerShell: $env:OPENAI_API_KEY = 'your-api-key-here'")
    print("CMD: set OPENAI_API_KEY=your-api-key-here")
    print()
    print("Get your API key from: https://platform.openai.com/api-keys")
    sys.exit(1)

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
