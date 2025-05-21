from typing import List, Union
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct
from qdrant_client import models
from core.config import settings
from core.exception import CustomException, ExceptionCase
from schemas.qdrant_schemas import DocumentInput, DocumentOutput


class QdrantService:
    def __init__(self, settings=settings):
        self.url = settings.QDRANT_SERVER
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.VECTOR_SIZE
        self.client = AsyncQdrantClient(url=self.url)

        if settings.DISTANCE_METRIC == "DOT":
            self.distance_metric = Distance.DOT
        elif settings.DISTANCE_METRIC == "COSINE":
            self.distance_metric = Distance.COSINE
        elif settings.DISTANCE_METRIC == "EUCLID":
            self.distance_metric = Distance.EUCLID
        elif settings.DISTANCE_METRIC == "MANHATTAN":
            self.distance_metric = Distance.MANHATTAN
        else:
            raise CustomException(
                ExceptionCase.INVALID_INPUT, detail="Invalid distance metric"
            )

    async def get_or_create_collection(self) -> None:
        """시스템 시작 시 컬렉션 확인 및 생성"""
        try:
            if not await self.client.collection_exists(self.collection_name):
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "size": self.vector_size,
                        "distance": self.distance_metric,
                    },
                )
        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.UNEXPECTED_ERROR, detail=str(e)
            )

    async def upsert_document(self, documents: List[DocumentInput]) -> None:
        """문서 청크 업로드"""
        try:
            points = [
                PointStruct(
                    id=document.id,
                    vector=document.embedding,
                    metadata=document.metadata,
                )
                for document in documents
            ]

            await self.client.upsert(
                collection_name=self.collection_name, points=points
            )

        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.UNEXPECTED_ERROR, detail=str(e)
            )

    async def query_document(
        self, embedding: List[float], metadata: dict
    ) -> List[DocumentOutput]:
        """임베딩 벡터로 문서 검색"""
        try:
            query_result = await self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key, match=models.MatchValue(value=value)
                        )
                        for key, value in metadata.items()
                    ]
                ),
            )
            query_points = query_result.points
            if not query_points:
                return []

            query_documents = [
                DocumentOutput(id=point.id, score=point.score, metadata=point.payload)
                for point in query_points
            ]
            return query_documents

        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.UNEXPECTED_ERROR, detail=str(e)
            )

    async def delete_document(self, conditions: Union[List[str], dict]) -> None:
        """Point ID로문서 삭제"""
        try:
            if isinstance(conditions, list):
                await self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=conditions),
                )
            elif isinstance(conditions, dict):
                await self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.Filter(
                        must=[
                            models.FieldCondition(
                                key=key, match=models.MatchValue(value=value)
                            )
                            for key, value in conditions.items()
                        ]
                    ),
                )
        except Exception as e:
            raise CustomException(
                exception_case=ExceptionCase.VECTOR_DB_DELETE_ERROR, detail=str(e)
            )
