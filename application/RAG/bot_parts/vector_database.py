import weaviate
from weaviate.classes.config import Configure,Property, DataType
from django.conf import settings
from RAG.bot_parts.voyageEmbedding import VoyageEmbeddings
from RAG.bot_parts.text_splitter import split_text

LANGS = ["uz", "en", "ru"]

class WeaviateDatabase:
    def __init__(self, wcd_url: str, wcd_api_key: str, voyage_model: str, company_name: str, chunk_size: int, chunk_overlap: int, path: str):
        self.path = path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.headers = {"X-VoyageAI-Api-Key": settings.VOYAGE_API_KEY}
        self.company_name = company_name
        self.voyage_model = voyage_model
        self.voyageAi = VoyageEmbeddings(api_key=settings.VOYAGE_API_KEY, model=voyage_model)
        self.client = self._create_client()
        self.collections = self._initialize_collections()

    def _create_client(self):
        return weaviate.connect_to_local(host="weaviate", port=8080, headers=self.headers)

    def _initialize_collections(self):
        self.client.collections.delete_all()

        print("Existing collections:", self.client.collections.list_all())
        collections = {}
        for lang in LANGS:
            collection_name = f"{self.company_name}_{lang}"
            print(f"Initializing collection: {collection_name}")
            collections[collection_name] = self._ensure_collection_exists(collection_name, lang)

        print("Final collections:", collections.keys())
        return collections

    def close(self):
        if self.client:
            self.client.close()

    def _ensure_collection_exists(self, collection_name, lang):
        try:
            print(f"Checking collection: {collection_name}")
            if not self.client.collections.exists(collection_name):
                print(f"Collection '{collection_name}' does not exist. Creating...")
                self.client.collections.create(
                    collection_name,
                    vectorizer_config=[
                        Configure.NamedVectors.text2vec_voyageai(
                            name="title_vector",
                            source_properties=["chunk_text"],
                            model="voyage-3",
                        )
                    ],
                    properties=[
                        Property(
                            name="chunk_text",
                            data_type=DataType.TEXT,
                            index_searchable=True,
                        ),
                        Property(
                            name="chunk_num",
                            data_type=DataType.INT,
                        )
                    ]
                )
                print(f"Collection '{collection_name}' created successfully.")
                self._prepare_document(collection_name, lang)
            else:
                print(f"Collection '{collection_name}' already exists.")

            return self.client.collections.get(collection_name)
        except Exception as e:
            print(f"Error ensuring collection '{collection_name}': {e}")
            return None

    def _prepare_document(self, company_name, lang):
        try:
            file_path = f"{self.path}/data/{self.company_name.lower()}/{lang}.txt"
            with open(file_path, "r") as file:
                text_data = file.read()

            doc_splits = split_text(text_data, chunk_size=self.chunk_size, overlap_sentences=self.chunk_overlap)
            print("-"*50)
            embeddings = self.voyageAi.embed_text(doc_splits)
            self._add_documents(company_name, doc_splits, embeddings)
            print("Documents successfully added to the database.")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error preparing documents: {e}")

    def _add_documents(self, company_name, documents, embeddings):
        try:
            collection = self.client.collections.get(company_name)
            with collection.batch.dynamic() as batch:
                for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
                    batch.add_object(
                        properties={"chunk_num": idx, "chunk_text": doc},
                        vector=embedding
                    )
            print(f"Added {len(documents)} documents to collection '{company_name}'.")
        except Exception as e:
            print(f"Error adding documents: {e}")

    def hybrid_query(self, query: str, company_name, limit=3):
        try:
            self.client = self._create_client()
            if company_name not in self.collections:
                print(f"Collection '{company_name}' not found.")
                return []

            vector = self.voyageAi.embed_text([query])[0]
            self.client.close() 
            response = self.collections[company_name].query.hybrid(
                query=query,
                limit=limit,
                vector=vector,
                alpha=0.3,
                query_properties = ["chunk_text"]
            )

            print("^"*30,response)
            return [obj.properties.get('chunk_text', '') for obj in response.objects]

        except Exception as e:
            print(f"Error during query: {e}")
            self.client.close() 
            return []
