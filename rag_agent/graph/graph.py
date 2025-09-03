from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from rag_agent.graph.chains.answer_grader import answer_grader
from rag_agent.graph.chains.hallucination_grader import hallucination_grader
from rag_agent.graph.chains.router import question_router
from rag_agent.graph.consts import RETRIEVE, GENERATE, GRADE_DOCUMENTS, WEBSEARCH
from rag_agent.graph.nodes.grade_documents import grade_documents
from rag_agent.graph.nodes.generate import generate
from rag_agent.graph.nodes.retireve import retrieve
from rag_agent.graph.nodes.web_search import web_search
from rag_agent.graph.state import GraphState

load_dotenv()


def should_continue(state: GraphState) -> str:
    if state["web_search"] == True:
        return WEBSEARCH
    return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def route_node(state: GraphState) -> str:
    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == WEBSEARCH:
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
        return RETRIEVE

workflow = StateGraph(GraphState)
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(WEBSEARCH, web_search)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)

workflow.set_conditional_entry_point(route_node, {RETRIEVE: RETRIEVE, WEBSEARCH: WEBSEARCH})
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)

workflow.add_conditional_edges(GRADE_DOCUMENTS, should_continue, {
    WEBSEARCH: WEBSEARCH, GENERATE: GENERATE
})

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,
        "useful": END,
        "not useful": WEBSEARCH,
    },
)

workflow.add_edge(GENERATE, END)
workflow.add_edge(WEBSEARCH, GENERATE)

app = workflow.compile()

if __name__ == "__main__":

    app.get_graph().draw_mermaid_png(output_file_path="graph.png")

    input_1 = "Tell me how to make chicken curry"
    input_2 = "Tell me about the F1 Movie"
    app.invoke(input={"question" : input_1})



    # for partial_response in app.stream(input={"question": "Tell me about F1 movie with streaming"},
    #                                    stream_mode="messages"):
    #     if partial_response[0].content:
    #         print(partial_response[0].content, end="|", flush=True)
