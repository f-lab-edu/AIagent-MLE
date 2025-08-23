"""
Langgraph의 사용자 정의 state를 정의하는 모듈.
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph

from schemas.schemas import Document


class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    username: Annotated[str, "user"]
    user_group: Annotated[str, "user_group"]
    question: Annotated[str, "question"]
    is_context_need: Annotated[bool, "is_context_need"]
    context: Annotated[Sequence[Document], "context"]
    old_context: Annotated[Sequence[Document], "old_context"]
    answer: Annotated[str, "answer"]


workflow = StateGraph(GraphState)
