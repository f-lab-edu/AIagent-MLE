from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance
from core.config import settings


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
            # 예외 처리
            # raise ValueError("Invalid distance metric")
            pass
