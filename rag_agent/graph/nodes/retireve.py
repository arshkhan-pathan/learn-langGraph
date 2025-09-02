from typing import Any, Dict

from rag_agent.graph.state import GraphState
from rag_agent.ingestion import retriever


def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]

    documents = retriever.invoke(question)

    print("-" * 10, "Documents", "-" * 10)
    print(documents)
    return {"documents": documents, "question": question}