# ReAct Agent with LangGraph

This directory contains an implementation of the **ReAct (Reasoning + Acting)** pattern using LangGraph, a framework for building stateful, multi-actor applications with LLMs.

## Overview

The ReAct pattern enables AI agents to:
1. **Reason** about what needs to be done
2. **Act** by using tools to accomplish tasks
3. **Iterate** through reasoning and acting until the goal is achieved

This implementation demonstrates how to build a ReAct agent using LangGraph's state management and conditional routing capabilities.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Entry Point  │───▶│  Agent Reason   │───▶│      Act        │
│                 │    │   (LLM + Tools) │    │  (Tool Node)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              └────────────┬────────────┘
                                           ▼
                                    ┌─────────────┐
                                    │   End or    │
                                    │  Continue?  │
                                    └─────────────┘
```

## Files

- **`main.py`** - Main application entry point and graph definition
- **`nodes.py`** - Graph nodes for reasoning and tool execution
- **`react.py`** - LLM configuration and tool definitions
- **`graph.png`** - Visual representation of the agent's workflow

## How It Works

1. **Entry Point**: The agent starts with a user message
2. **Reasoning Node**: The LLM analyzes the request and decides what tools to use
3. **Action Node**: Tools are executed based on the LLM's decisions
4. **Conditional Routing**: The agent decides whether to continue reasoning or end
5. **Iteration**: If more actions are needed, the process repeats

## Tools Available

- **TavilySearch**: Web search capability for gathering information
- **triple**: A custom tool that multiplies a number by 3

## Usage

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Set up environment variables:
   ```bash
   # Create a .env file with:
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

### Running the Agent

```bash
cd react_agent
python main.py
```

### Example Query

The agent can handle complex queries like:
```
"what is the weather in sf? List it and then Triple it"
```

This demonstrates the agent's ability to:
1. Search for current weather information
2. Process the results
3. Apply mathematical operations

## Key Features

- **Stateful Workflow**: Maintains conversation context throughout the reasoning process
- **Conditional Logic**: Automatically determines when to continue or end based on tool usage
- **Tool Integration**: Seamlessly combines external APIs with custom functions
- **Visual Graph**: Generates a Mermaid diagram showing the agent's workflow

## Customization

### Adding New Tools

To add new tools, modify `react.py`:

```python
@tool
def your_custom_tool(param: str) -> str:
    """Description of what your tool does"""
    # Your tool logic here
    return result

tools = [TavilySearch(max_results=1), triple, your_custom_tool]
```

### Modifying the Reasoning Engine

Customize the system message in `nodes.py` to change the agent's behavior:

```python
SYSTEM_MESSAGE = """
You are a specialized assistant for [your domain].
[Add specific instructions here]
"""
```

## Dependencies

- `langgraph` - Graph-based workflow framework
- `langchain-openai` - OpenAI LLM integration
- `langchain-tavily` - Web search tool
- `python-dotenv` - Environment variable management

## Related Projects

This implementation is part of a larger collection of LangGraph examples:
- **reflection/** - Reflection-based reasoning
- **reflexion/** - Reflexion pattern implementation

## Learn More

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/) 