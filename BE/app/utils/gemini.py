from typing import Literal, List
from google import genai
from google.genai import types
from core.config import settings
from core.exception import CustomException, ExceptionCase


class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.vector_size = settings.VECTOR_SIZE
        self.model_name = "gemini-2.0-flash"
        self.embedding_model_name = "gemini-embedding-exp-03-07"

    async def generate_contents(self, contents: str) -> str:
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
