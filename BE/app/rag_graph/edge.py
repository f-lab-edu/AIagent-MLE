"""
Langgraph에서 Node를 그래프에 추가하고 Edge를 연결하는 모듈.
"""

from langgraph.graph import START, END
from langgraph.graph.state import CompiledStateGraph
from rag_graph.node import (
    node_check_context_latest,
    node_decision_context_need,
    node_get_latest_context,
    node_llm_invoke,
    node_refine_question,
    node_retriever,
    router_decision_context_need,
)
from rag_graph.state import workflow
from core.exception import CustomException, ExceptionCase


def get_graph() -> CompiledStateGraph:
    """
    state에 노드와 에지를 추가 후 컴파일된 그래프 객체 반환.
    """
    try:
        workflow.add_node("refine_question", node_refine_question)
        workflow.add_node("decision_context_need", node_decision_context_need)
        workflow.add_node("retriever", node_retriever)
        workflow.add_node("check_context_latest", node_check_context_latest)
        workflow.add_node("get_latest_context", node_get_latest_context)
        workflow.add_node("llm_invoke", node_llm_invoke)

        workflow.add_edge(START, "refine_question")
        workflow.add_edge("refine_question", "decision_context_need")
        workflow.add_conditional_edges(
            "decision_context_need",
            router_decision_context_need,
            {True: "retriever", False: "llm_invoke"},
        )
        workflow.add_edge("retriever", "check_context_latest")
        workflow.add_edge("check_context_latest", "get_latest_context")
        workflow.add_edge("get_latest_context", "llm_invoke")
        workflow.add_edge("llm_invoke", END)

        graph = workflow.compile()

        return graph
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_EDGE_ERROR,
            detail=f"Error occured in get_graph: {e}",
        )
