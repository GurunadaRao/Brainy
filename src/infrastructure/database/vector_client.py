from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from src.configs.settings import settings


class VectorClient:
    def __init__(self) -> None:
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self.collection_name = "transcript_chunks"
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure the target collection exists in Qdrant with correct dimensions."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # nomic-embed-text generates 768 dimensions
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=768,
                        distance=qdrant_models.Distance.COSINE
                    )
                )
                print(f"Qdrant: Created collection '{self.collection_name}'")
        except Exception as e:
            print(f"Qdrant: Collection initialization failed: {e}")

    def upsert_chunk(self, chunk_id: int, embedding: list, payload: dict) -> None:
        """Upsert a single chunk embedding and its metadata payload into Qdrant."""
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
        except Exception as e:
            raise RuntimeError(f"Qdrant: Failed to upsert chunk {chunk_id}: {e}")

    def search_chunks(self, query_embedding: list, top_k: int = 5) -> list:
        """Search for the most similar chunks to the query embedding."""
        try:
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k
            )
            return [
                {
                    "chunk_id": hit.id,
                    "content": hit.payload.get("content", ""),
                    "video_id": hit.payload.get("video_id", ""),
                    "score": hit.score
                }
                for hit in response.points
            ]
        except Exception as e:
            raise RuntimeError(f"Qdrant: Search query failed: {e}")


# Global vector client instance
vector_client = VectorClient()
