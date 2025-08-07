"""
Gemini 서비스 객체 생성 모듈
"""

from typing import Literal, List
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from typing import Sequence
from core.config import settings
from core.exception import CustomException, ExceptionCase


class GeminiService:
    def __init__(
        self,
        model: Literal[
            "gemini-2.0-flash", "gemini-2.0-flash-lite"
        ] = "gemini-2.0-flash",
    ):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.vector_size = settings.VECTOR_SIZE
        self.model_name = model
        self.embedding_model_name = "gemini-embedding-001"

        # langgraph 모델
        self.model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0,
            max_output_tokens=8192,
            max_retries=10,
        )

    async def generate_contents(self, contents: str) -> str:
        """
        low-level gemini api
        """
        try:
            result = await self.client.aio.models.generate_content(
                model=self.model_name, contents=contents
            )
            return result.text
        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.GEMINI_ERROR, detail=str(e)
            )

    async def generate_embedding(
        self, contents: str, task: Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]
    ) -> List[float]:
        """
        low-level gemini api
        """
        try:
            result = await self.client.aio.models.embed_content(
                model=self.embedding_model_name,
                contents=contents,
                config=types.EmbedContentConfig(task_type=task),
            )
            return result.embeddings[0].values
        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.GEMINI_ERROR, detail=str(e)
            )

    async def ainvoke(self, inputs: Sequence[BaseMessage]) -> str:
        """
        langgraph model api
        """
        try:
            result = await self.model.ainvoke(inputs)
            return result.content
        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.GEMINI_ERROR, detail=str(e)
            )
