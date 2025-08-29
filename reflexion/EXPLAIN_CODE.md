# Reflexion Agent Code Explanation

## Overview
The `reflexion` directory contains a sophisticated LangGraph-based agent that implements the **Reflexion architecture** - an advanced pattern for generating high-quality responses through self-reflection, external tool usage, and iterative improvement. This is a more complex and powerful implementation compared to the basic reflection pattern.

## Architecture

### Core Concept
The Reflexion agent implements a **research and refinement loop** with three main components:
1. **Draft Node**: Generates initial response with self-reflection
2. **Tool Execution Node**: Researches information using external tools
3. **Revise Node**: Refines response based on research findings and previous critique

### Graph Structure
```
START → DRAFT → EXECUTE_TOOLS → REVISE → EXECUTE_TOOLS → REVISE → ... → END
```

The agent runs for a maximum of 2 iterations (configurable via `MAX_ITERATIONS`).

## Code Components

### 1. `main.py` - Graph Orchestration

#### State Management:
```python
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
```

**Purpose**: Maintains conversation history and tool execution results throughout the process.

#### Key Functions:
- **`draft_node(state)`**: Creates initial response using the first responder chain
- **`execute_tools_node(state)`**: Runs research queries using external tools
- **`revise_node(state)`**: Refines response based on research findings
- **`event_loop(state)`**: Controls iteration flow based on tool usage count

#### Graph Building:
```python
builder = StateGraph(State)
builder.add_node("draft", draft_node)
builder.add_node("execute_tools", execute_tools_node)
builder.add_node("revise", revise_node)

builder.add_edge(START, "draft")
builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "revise")
builder.add_conditional_edges("revise", event_loop, {END: END, "execute_tools": "execute_tools"})
```

#### Example Usage:
```python
res = graph.invoke({
    "messages": [
        "Write about AI-Powered SOC / autonomous soc problem domain, list startups that do that and raised capital."
    ]
})
```

### 2. `chains.py` - LLM Chain Definitions

#### Actor Prompt Template:
```python
actor_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. Recommend search queries to research information and improve your answer."""),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Answer the user's question above using the required format."),
])
```

**Purpose**: Base template for both first responder and revisor chains.

#### First Responder Chain:
```python
first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="Provide a detailed ~250 word answer."
)

first_responder = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)
```

**Purpose**: Generates initial response with self-reflection and search query recommendations.

#### Revisor Chain:
```python
revise_instructions = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
        - You MUST include numerical citations in your revised answer to ensure it can be verified.
        - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
            - [1] https://example.com
            - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
"""

revisor = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")
```

**Purpose**: Refines the answer using research findings and previous critique.

#### LLM Configuration:
- Uses OpenAI's GPT-4o-mini model
- Implements structured output parsing with Pydantic models

### 3. `schemas.py` - Data Models

#### Reflection Model:
```python
class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing.")
    superfluous: str = Field(description="Critique of what is superfluous")
```

**Purpose**: Captures self-critique for improvement guidance.

#### AnswerQuestion Model:
```python
class AnswerQuestion(BaseModel):
    answer: str = Field(description="~250 word detailed answer to the question.")
    reflection: Reflection = Field(description="Your reflection on the initial answer.")
    search_queries: List[str] = Field(description="1-3 search queries for researching improvements to address the critique of your current answer.")
```

**Purpose**: Structured output for initial response generation.

#### ReviseAnswer Model:
```python
class ReviseAnswer(AnswerQuestion):
    references: List[str] = Field(description="Citations motivating your updated answer.")
```

**Purpose**: Enhanced output for revised responses with citations.

### 4. `tool_executor.py` - External Tool Integration

#### Search Tool:
```python
tavily_tool = TavilySearch(max_results=5)

def run_queries(search_queries: list[str], **kwargs):
    """Run the generated queries."""
    return tavily_tool.batch([{"query": query} for query in search_queries])
```

**Purpose**: Executes research queries using Tavily search engine.

#### Tool Node:
```python
execute_tools = ToolNode([
    StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
    StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
])
```

**Purpose**: Integrates search functionality into the LangGraph workflow.

## How It Works

### 1. Initial Draft
- User provides research question
- First responder generates ~250 word answer
- Self-reflection identifies areas for improvement
- Search queries are generated for research

### 2. Research Phase
- Tool execution node runs search queries
- Gathers relevant information from web sources
- Results are added to conversation state

### 3. Revision Loop
- Revisor analyzes research findings
- Refines answer based on new information
- Adds citations and removes superfluous content
- Process repeats up to 2 times

### 4. Termination
- Process ends after maximum iterations
- Final output includes verified citations and refined content

## Use Cases

### Primary Use Case: Research and Writing
- **Academic writing** with citations
- **Market research** reports
- **Technical documentation** with verification
- **Content creation** requiring factual accuracy

### Benefits:
- **Research-backed**: Uses external tools for information gathering
- **Self-improving**: Multiple iterations with self-critique
- **Verifiable**: Includes citations and references
- **Quality-focused**: Structured output with word limits

## Key Differences from Reflection

1. **Complex Architecture**: Uses StateGraph with structured state management
2. **External Tools**: Integrates web search for research
3. **Structured Output**: Pydantic models for reliable data handling
4. **Citation System**: Includes references and verification
5. **Research Focus**: Designed for factual, research-based responses

## Configuration

### Environment Variables:
```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here  # Optional, for tracing
LANGCHAIN_TRACING_V2=true                      # Optional
LANGCHAIN_PROJECT=reflexion agent               # Optional
```

### Customization Points:
- **Maximum iterations**: Modify `MAX_ITERATIONS` constant
- **Search results**: Adjust `max_results` in TavilySearch
- **Word limits**: Update field descriptions in schemas
- **LLM model**: Change model in `chains.py`

## Running the Code

1. Set up environment variables
2. Install dependencies: `pip install langgraph langchain-openai python-dotenv tavily-python`
3. Run: `python main.py`

## Example Output Flow

```
Input: "Write about AI-Powered SOC / autonomous soc problem domain, list startups that do that and raised capital."

Iteration 1:
- Draft: Creates initial 250-word answer with self-critique
- Execute Tools: Researches AI-Powered SOC startups and funding
- Revise: Refines answer using research findings

Iteration 2:
- Execute Tools: Additional research if needed
- Revise: Final refinement with citations
- End: Process completes with verified, cited response
```

## Advanced Features

### Structured Output Parsing:
- Uses OpenAI's function calling for reliable output
- Pydantic validation ensures data integrity
- Consistent format across iterations

### Research Integration:
- Automated web search for verification
- Citation management for credibility
- Fact-checking through multiple sources

### Iterative Improvement:
- Self-reflection for quality assessment
- Research-driven content enhancement
- Citation-based verification system

This Reflexion pattern is excellent for research-intensive tasks where factual accuracy, citations, and iterative improvement are crucial for producing high-quality, verifiable content. 