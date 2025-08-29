from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from chains import revisor, first_responder
from tool_executor import execute_tools


# Define state schema
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


MAX_ITERATIONS = 2


def draft_node(state: State):
    response = first_responder.invoke(state["messages"])
    return {"messages": [response]}


def execute_tools_node(state: State):
    # Fixed: ToolNode.invoke() expects state, returns state
    return execute_tools.invoke(state)


def revise_node(state: State):
    response = revisor.invoke(state["messages"])
    return {"messages": [response]}


def event_loop(state: State) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state["messages"])
    if count_tool_visits > MAX_ITERATIONS:
        return END
    return "execute_tools"


# Build the graph
builder = StateGraph(State)
builder.add_node("draft", draft_node)
builder.add_node("execute_tools", execute_tools_node)
builder.add_node("revise", revise_node)

builder.add_edge(START, "draft")
builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "revise")
builder.add_conditional_edges("revise", event_loop, {END: END, "execute_tools": "execute_tools"})

graph = builder.compile()

print(graph.get_graph().draw_mermaid())

res = graph.invoke({
    "messages": [
        "Write about AI-Powered SOC / autonomous soc problem domain, list startups that do that and raised capital."]
})

print(res["messages"][-1].tool_calls[0]["args"]["answer"])
print(res)
