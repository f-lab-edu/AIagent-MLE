"""
llm 프롬프트 생성 함수 모음
"""

from typing import Sequence, Optional
from schemas.schemas import Document
from utils.datasource_url import context_url
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def refine_question(messages: Sequence[BaseMessage]) -> Sequence[BaseMessage]:
    """
    1. 이전 대화 내역을 바탕으로 쿼리를 재작성 해주는 노드에 사용되는 프롬프트.
    """

    system = """You are an AI assistant who refines the user's question.
Reflecting on the given "previous conversation", please reconstruct the last "user question" into a complete question that can be understood independently.
If the last question is already complete, please rewrite it as is. Do not add any other explanation."""

    return [
        SystemMessage(content=system),
        *messages,
    ]


def check_context_need(question: HumanMessage) -> Sequence[BaseMessage]:
    """
    2. 쿼리를 보고 컨텍스트 검색이 필요한지 결정하는 노드에 사용되는 프롬프트.
    """

    system = """Look at the user question and decide if it needs context in the Vector Store or if it is a simple answer that can be answered right away.
The Vector Store contains various projects and internal information from our company.
For questions about this information, check the context. For simple answers that do not, context is not needed."""
    return [
        SystemMessage(content=system),
        question,
    ]


def check_context_latest(context: Sequence[Document]) -> Sequence[BaseMessage]:
    """
    4. 컨텍스트의 최신성을 검증하는 노드에 사용되는 프롬프트. (MCP 호출)
    """

    doc_metadata_dict = {}

    for doc in context:
        data_source = doc.datasource
        page_id = doc.page_id

        if data_source not in doc_metadata_dict:
            doc_metadata_dict[data_source] = []

        doc_metadata_dict[data_source].append(page_id)

    prompt = """Retrieve page metadata and properties from a specified data source using each page's ID. Use the appropriate tool.\n\n"""
    for i, (data_source, page_id_list) in enumerate(doc_metadata_dict.items()):
        prompt += f"""**{i + 1}. Data Source: {data_source}**\n- page id: {", ".join(page_id_list)}\n\n"""

    return [
        HumanMessage(content=prompt),
    ]


def get_latest_context() -> Sequence[BaseMessage]:
    """
    5. 최신 컨텍스트를 가져오는 노드에 사용되는 프롬프트.
    """
    return


def llm_answer(
    question: str,
    messages: Sequence[BaseMessage],
    context: Optional[Sequence[Document]],
) -> Sequence[BaseMessage]:
    """
    6. 최종 llm 답변 노드에 사용되는 프롬프트.
    """

    system = """### Role and Basic Instructions
You are a professional AI assistant who answers users' questions based on information stored in a vector database.
Your job is to generate answers that are accurate, friendly, and helpful, making the most of the information provided.

**Answer Generation Rules:**
- If there is a context provided, answer based on that context.
- If there is no context provided, answer the question directly.
- Please write your answers in clear and understandable sentences.
- If there is a document that is the basis for your answer, be sure to cite the source at the end of your answer in the format "[Source: {document url}]". If you referenced multiple documents, please cite them all."""

    human_prompt_parts = []

    chat_history_lines = []
    for message in messages:
        chat_history_lines.append(f"{message.type}: {message.content}")
    chat_history = "\n".join(chat_history_lines)
    if not chat_history:
        chat_history = "No previous conversation"

    human_prompt_parts.append(f"### Chat History:\n{chat_history}")
    human_prompt_parts.append(f"### Question:\n{question}")

    if context:
        context_parts = []
        context_parts.append("### Context:\n")
        for i, document in enumerate(context):
            context_prompt = f"""**Document {i + 1}**
- datasource_url: {context_url(document.datasource, document.page_id)}
- content: {document.content}"""
            context_parts.append(context_prompt)
        context_str = "\n".join(context_parts)
        human_prompt_parts.append(context_str)

    human_prompt = "\n\n---\n\n".join(human_prompt_parts)

    return [
        SystemMessage(content=system),
        HumanMessage(content=human_prompt),
    ]
