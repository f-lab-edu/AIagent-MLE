from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance
from core.config import settings
from core.exception import CustomException, ExceptionCase


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
                self.client.create_collection(
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
