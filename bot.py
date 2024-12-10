from bot_parts.voyageEmbedding import VoyageEmbeddings
from bot_parts.vector_database import QdrantDatabase
from bot_parts.lmm import contextualize_question, answer_question
from bot_parts.query_database import initialize_database, get_session_history, append_to_session_history
from qdrant_client.http.models import Distance
import api_keys

DB_PATH = "http://localhost:6333"
CORE_COLLECTION = "CoreData"
VECTOR_SIZE = 1024
DISTANCE_METRIC = Distance.DOT

core_db = QdrantDatabase(DB_PATH, CORE_COLLECTION, VECTOR_SIZE, distance_metric=DISTANCE_METRIC)
voyageAi = VoyageEmbeddings(api_key=api_keys.voyage_api_key, model="voyage-multilingual-2")

def query_core_data(query: str, top_k: int = 5) -> str:
    """Query the core database."""

    # print(f"### {query} ####")
    query_embedding = voyageAi.embed_text(texts=[query])[0]
    results = core_db.query(query_embedding, top_k)
    return "\n".join([result.payload.get("text", "No payload found") for result in results])

def ask_question(session_id: str, user_input: str) -> str:
    initialize_database()
    """Handle a user's question."""
    chat_history = get_session_history(session_id)
    standalone_question = contextualize_question(
        [f"User: {u}\nAssistant: {a}" for u, a in chat_history],
        user_input
    )
    context = query_core_data(standalone_question)
    response = answer_question(context, standalone_question)

    append_to_session_history(session_id, user_input, response)
    return str(response)

# if __name__ == "__main__":
    # print(ask_question("1132", "Ismim javlon faamiliyam Valiev, 2 yillik tajribam bor, HTML CSS JS Vue Js typescript tailwind Fast API va shu kabilarni bilaman"))
