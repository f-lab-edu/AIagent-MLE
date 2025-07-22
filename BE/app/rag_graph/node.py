"""
Langgraph에서 Node를 정의하는 모듈
"""

from rag_graph.state import GraphState
from rag_graph import prompt, output_structure
from services.gemini import GeminiService
from services.qdrant_service import QdrantService
from services.mcp_service import agent
from schemas.schemas import Document, DocumentMetadata
from utils.data_loader import get_data_loader
from core.exception import CustomException, ExceptionCase


gemini = GeminiService()
qdrant = QdrantService()


async def node_refine_question(state: GraphState) -> GraphState:
    """
    1. 이전 대화 내역을 바탕으로 쿼리를 재작성 해주는 노드.
    """
    try:
        print("-------------------------")
        print(node_refine_question.__name__)
        print(state)
        gemini = GeminiService(model="gemini-2.0-flash-lite")
        messages = state["messages"]

        input_prompt = prompt.refine_question(messages)
        model = gemini.model.with_structured_output(output_structure.RefineQuestion)

        result = await model.ainvoke(input_prompt)
        rewritten_question = result.rewritten_question
        return GraphState(question=rewritten_question)
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_NODE_ERROR,
            detail=f"Error occured in node_refine_question: {e}",
        )


async def node_decision_context_need(state: GraphState) -> GraphState:
    """
    2. 쿼리를 보고 컨텍스트 검색이 필요한지 결정하는 노드.
    """
    try:
        print("-------------------------")
        print(node_decision_context_need.__name__)
        print(state)
        gemini = GeminiService(model="gemini-2.0-flash-lite")
        question = state["question"]

        input_prompt = prompt.check_context_need(question=question)
        model = gemini.model.with_structured_output(output_structure.RouteQuery)

        result = await model.ainvoke(input_prompt)
        decision = result.decision
        if decision == "context required":
            return GraphState(is_context_need=True)
        else:
            return GraphState(is_context_need=False)
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_NODE_ERROR,
            detail=f"Error occured in node_decision_context_need: {e}",
        )


def router_decision_context_need(state: GraphState) -> bool:
    """
    검색이 필요 여부에 따라 다음 노드를 결정하는 라우터.
    """
    print("-------------------------")
    print(router_decision_context_need.__name__)
    print(state)

    return state["is_context_need"]


async def node_retriever(state: GraphState) -> GraphState:
    """
    3. 쿼리를 바탕으로 컨텍스트를 가져오는 노드.
    """
    try:
        print("-------------------------")
        print(node_retriever.__name__)
        print(state)
        question = state["question"]
        authority_group = state["authority_group"]

        embedding = await gemini.generate_embedding(
            contents=question, task="RETRIEVAL_QUERY"
        )
        output_documents = await qdrant.query_document(
            embedding=embedding,
            metadata=DocumentMetadata(authority_group=authority_group),
        )
        documents = [
            Document(
                content=output_document.metadata.content,
                datasource=output_document.metadata.datasource,
                updated_at=output_document.metadata.updated_at,
                page_id=output_document.metadata.page_id,
            )
            for output_document in output_documents
        ]

        return GraphState(context=documents)
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_NODE_ERROR,
            detail=f"Error occured in node_retriever: {e}",
        )


async def node_check_context_latest(state: GraphState) -> GraphState:
    """
    4. 컨텍스트의 최신성을 검증하는 노드.
    최신이 아닌 컨텍스트는 mcp를 호출해서 최신 정보로 업데이트.
    """
    try:
        print("-------------------------")
        print(node_check_context_latest.__name__)
        print(state)
        latest_context = []
        old_context = []

        context = state["context"]
        input_prompt = prompt.check_context_latest(context)
        async with agent.create_agent(
            response_format=output_structure.CheckContextLatestList
        ) as check_context_latest_agent:
            messages = {"messages": input_prompt}
            response = await check_context_latest_agent.ainvoke(input=messages)
            context_for_check = response["structured_response"].data

        for document in context:
            data_source = document.datasource
            page_id = document.page_id
            last_edited_time = document.updated_at

            for check_info in context_for_check:
                if (
                    check_info.data_source == data_source
                    and check_info.page_id == page_id
                ):
                    if last_edited_time != check_info.last_edited_time:
                        old_context.append(document)
                    else:
                        latest_context.append(document)
                    break

        return GraphState(context=latest_context, old_context=old_context)
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_NODE_ERROR,
            detail=f"Error occured in node_check_context_latest: {e}",
        )


async def node_get_latest_context(state: GraphState) -> GraphState:
    """
    5. 최신 컨텍스트를 가져오는 노드.
    """
    try:
        print("-------------------------")
        print(node_get_latest_context.__name__)
        print(state)
        latest_context = state["context"]
        old_context = state["old_context"]
        for context in old_context:
            datasource = context.datasource
            page_id = context.page_id
            data_loader = get_data_loader(datasource)
            if data_loader:
                new_context = await data_loader.get_documents(
                    page_id=page_id, recursive_page=False
                )
            else:
                return GraphState(context=latest_context)

            latest_context.extend(new_context)

        return GraphState(context=latest_context)
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_NODE_ERROR,
            detail=f"Error occured in node_get_latest_context: {e}",
        )


async def node_llm_invoke(state: GraphState) -> GraphState:
    """
    6. 최종 llm 답변 노드.
    """
    try:
        print("-------------------------")
        print(node_llm_invoke.__name__)
        print(state)
        question = state["question"]
        context = state["context"]
        messages = state["messages"]

        input_prompt = prompt.llm_answer(question, messages, context)
        result = await gemini.model.ainvoke(input_prompt)

        return GraphState(answer=result)
    except Exception as e:
        raise CustomException(
            exception_case=ExceptionCase.GRAPH_NODE_ERROR,
            detail=f"Error occured in node_llm_invoke: {e}",
        )
