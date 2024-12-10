from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, ScoredPoint
from qdrant_client.models import PointStruct

class QdrantDatabase:
    def __init__(self, db_path: str, collection_name: str, vector_size: int, distance_metric: Distance):
        self.client = QdrantClient(url=db_path)
        self.collection_name = collection_name
        self._ensure_collection_exists(vector_size, distance_metric)

    def _ensure_collection_exists(self, vector_size: int, distance_metric: Distance):
        try:
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            if "not found" in str(e).lower():
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=distance_metric),
                )
                print(f"Collection '{self.collection_name}' created successfully.")
            else:
                raise

    def add_documents(self, embeddings: list[list[float]], documents):
        for index, embedding in enumerate(embeddings):
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(id=index, vector=embedding, payload={"text": documents[index]}),
                ],
            )

    def query(self, query_embedding: list[float], top_k: int = 3) -> list[ScoredPoint]:
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
