import requests
import math

class VoyageEmbeddings:
    def __init__(self, api_key,model, endpoint="https://api.voyageai.com/v1/embeddings",):
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model

    def embed_text(self, texts, batch_size=10):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        all_embeddings = []
        num_batches = math.ceil(len(texts) / batch_size)

        for i in range(num_batches):
            batch_texts = texts[i * batch_size:(i + 1) * batch_size]
            payload = {
                "input": batch_texts,
                "model": self.model
            }
            try:
                response = requests.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                for item in data['data']:
                    all_embeddings.append(item['embedding'])
            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Failed to retrieve embeddings for batch {i + 1}: {e}")

        return all_embeddings
