"""
Langgraph에서 Node를 그래프에 추가하고 Edge를 연결하는 모듈.
"""

from langgraph.graph import START, END
from langgraph.graph.state import CompiledStateGraph
from rag_graph.node import (
    refine_question,
    decide_context_necessity,
    retrieve_context,
    check_context_latest,
    update_old_context,
    generate_answer,
    should_retrieve_context,
)
from rag_graph.state import workflow
from core.exception import CustomException, ExceptionCase


def get_graph() -> CompiledStateGraph:
    """
    state에 노드와 에지를 추가 후 컴파일된 그래프 객체 반환.
    """
    try:
        workflow.add_node("retrieve_context", retrieve_context)
        workflow.add_node("refine_question", refine_question)
        workflow.add_node("decide_context_necessity", decide_context_necessity)
        workflow.add_node("check_context_latest", check_context_latest)
        workflow.add_node("update_old_context", update_old_context)
        workflow.add_node("generate_answer", generate_answer)

        workflow.add_edge(START, "refine_question")
        workflow.add_edge("refine_question", "decide_context_necessity")
        workflow.add_conditional_edges(
            "decide_context_necessity",
            should_retrieve_context,
            {True: "retrieve_context", False: "generate_answer"},
        )
        workflow.add_edge("retrieve_context", "check_context_latest")
        workflow.add_edge("check_context_latest", "update_old_context")
        workflow.add_edge("update_old_context", "generate_answer")
        workflow.add_edge("generate_answer", END)

        graph = workflow.compile()

        return graph
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_EDGE_ERROR,
            detail=f"Error occured in get_graph: {e}",
        )
