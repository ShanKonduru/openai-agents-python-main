# OpenAI Agents SDK Python - Workspace Overview

## **Project Purpose**

This is the official Python implementation of the OpenAI Agents SDK - a lightweight, production-ready framework for building multi-agent AI workflows. It's designed as an upgrade from OpenAI's experimental "Swarm" framework, providing a minimal set of powerful primitives for building real-world agentic applications.

## **Core Architecture & Concepts**

### **1. Agents** - The central building blocks

- LLMs configured with instructions, tools, and handoffs
- Support for structured outputs using Pydantic models
- Context-aware with dependency injection
- Configurable with custom models and settings

### **2. Handoffs** - Inter-agent delegation

- Allows agents to transfer control to specialized agents
- Supports input filtering and custom callbacks
- Two main patterns: Manager/Orchestrator and Peer handoffs

### **3. Guardrails** - Safety and validation

- Input and output validation running in parallel
- Tripwire mechanism for immediate execution halting
- Support for custom validation logic

### **4. Sessions** - Conversation memory

- Automatic conversation history management
- Multiple backends: SQLite, Redis, custom implementations
- Eliminates manual state handling between turns

### **5. Tools** - Agent capabilities

- Function tools: Convert any Python function to an agent tool
- Hosted tools: Web search, file search, computer use, code interpreter
- Agent tools: Use other agents as tools
- MCP integration: Model Context Protocol support

### **6. Tracing** - Observability

- Built-in comprehensive tracing system
- Integration with OpenAI's Traces dashboard
- Support for external processors (Logfire, AgentOps, Braintrust, etc.)
- Custom span creation capabilities

## **Design Patterns Demonstrated**

**Examples show multiple architectural patterns:**

1. **Deterministic Flows** - Sequential agent execution with gates/conditions
2. **Routing/Triage** - Central dispatcher routing to specialized agents  
3. **Agents as Tools** - Agents calling other agents as tools vs handoffs
4. **LLM-as-a-Judge** - Using LLMs to evaluate and improve outputs
5. **Parallelization** - Running multiple agents concurrently
6. **Streaming** - Real-time response streaming
7. **Memory Management** - Persistent conversation history

## **Key Features**

- **Provider Agnostic**: Works with OpenAI and 100+ other LLMs via LiteLLM
- **Minimal Abstractions**: Small learning curve with powerful primitives
- **Production Ready**: Built-in error handling, timeouts, retries
- **Streaming Support**: Real-time response generation
- **Voice Integration**: Speech-to-text and text-to-speech capabilities
- **MCP Integration**: Model Context Protocol for external tool access
- **Flexible Context**: Dependency injection for state management
- **Comprehensive Examples**: From basic hello world to complex multi-agent systems

## **Installation**

### **Option 1: Install with pip (recommended)**

```bash
pip install openai-agents
```

### **Option 2: Install from requirements**

```bash
# For minimal installation (compatible with existing packages)
pip install -r requirements-minimal.txt

# For full installation
pip install -r requirements.txt
```

### **Option 3: Install with optional dependencies**

```bash
# For voice support
pip install 'openai-agents[voice]'

# For Redis session support
pip install 'openai-agents[redis]'

# For visualization
pip install 'openai-agents[viz]'
```

## **Quick Start Examples**

### **Hello World**

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

### **Function Tools**

```python
import asyncio
from agents import Agent, Runner, function_tool

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

agent = Agent(
    name="Weather Assistant",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)

async def main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### **Handoffs Example**

```python
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)

async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?

if __name__ == "__main__":
    asyncio.run(main())
```

## **Development Workflow**

### **Setup Environment**

```bash
# Activate environment
.\002_activate.bat

# Install dependencies
.\003_setup.bat

# Run examples
.\004_run.bat <script_name>
```

### **Project Structure**

- **Source code**: Implementation in the agents package
- **Tests**: Comprehensive test suite with snapshot testing
- **Examples**: Organized by complexity and use case
  - `examples/basic/` - Hello world, tools, lifecycle
  - `examples/agent_patterns/` - Design patterns
  - `examples/customer_service/` - Multi-agent systems
  - `examples/research_bot/` - Complex workflows
  - `examples/voice/` - Speech integration
  - `examples/mcp/` - External tool integration
- **Documentation**: Comprehensive docs with multi-language support
- **Utilities**: Development commands and scripts

## **Notable Examples**

### **Basic Examples**

- **Hello World**: Simple agent interactions
- **Tools**: Function calling and tool usage
- **Lifecycle**: Agent execution management

### **Advanced Patterns**

- **Customer Service**: Multi-agent airline support system
- **Research Bot**: Parallel web search and report generation
- **Financial Research**: Complex multi-step analysis
- **Voice Integration**: Real-time speech interfaces

### **Integration Examples**

- **MCP Examples**: Filesystem, Git, and other external integrations
- **Memory Examples**: SQLite, Redis, encrypted sessions
- **Model Providers**: Various LLM integrations

## **Documentation**

The project includes extensive documentation covering:

- **Quickstart guides**: Getting started quickly
- **Core concepts**: Agents, handoffs, tools, guardrails
- **Advanced patterns**: Streaming, tracing, sessions
- **API reference**: Complete API documentation
- **Multi-language support**: English, Japanese, Korean, Chinese

### **Online Documentation**

- **Homepage**: <https://openai.github.io/openai-agents-python/>
- **Repository**: <https://github.com/openai/openai-agents-python>

## **Key Design Principles**

1. **Enough features to be worth using, but few enough primitives to make it quick to learn**
2. **Works great out of the box, but you can customize exactly what happens**

## **Dependencies**

### **Core Dependencies**

- OpenAI Python client (>=2.2,<3)
- Pydantic for data validation (>=2.10,<3)
- Griffe for docstring parsing
- Typing extensions
- Requests for HTTP

### **Optional Dependencies**

- **Voice**: numpy, websockets
- **Visualization**: graphviz
- **Database**: SQLAlchemy, asyncpg
- **Caching**: Redis
- **Security**: cryptography

## **Development Tools**

- **Package Management**: uv
- **Code Quality**: ruff (formatter/linter), mypy (type checking)
- **Testing**: pytest, pytest-asyncio
- **Documentation**: MkDocs with Material theme
- **Coverage**: Built-in coverage reporting

## **Environment Requirements**

- Python 3.9 or newer
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

This workspace represents a mature, well-architected framework that balances simplicity with power, making it suitable for both prototyping and production deployment of multi-agent AI systems.