import time
from RAG.bot_parts.vector_database import WeaviateDatabase
from RAG.bot_parts.gemini_llm import contextualize_question, answer_question
from RAG.bot_parts.query_database import (
    initialize_database,
    get_session_history,
    append_to_session_history,
)

class DocumentHandler:
    def __init__(self, db_url: str, db_api_key: str, company_name: str, path: str, chunk_size: int, chunk_overlap: int):
        """Initializes the document handler with a vector database client and prepares the database."""
        self.company_name = company_name
        self.client = WeaviateDatabase(
            wcd_api_key=db_api_key, 
            wcd_url=db_url, 
            voyage_model="voyage-3-large",
            company_name=company_name, 
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap, 
            path=path
        )
        initialize_database(path=self.client.path)

    def close(self):
        """Closes the database client."""
        self.client.close()

    def query_core_data(self, query: str, lang: str) -> str:
        """Queries the database for relevant information."""
        results = self.client.hybrid_query(query=query, company_name=f"{self.company_name}_{lang}")
        return "\n".join(results) if results else "No relevant data found."

    def ask_question(self, session_id: str, user_input: str):
        """Handles user queries by contextualizing the question, fetching relevant data, and generating a response."""
        start_time = time.time()

        # Retrieve chat history
        chat_history = get_session_history(session_id,path=self.client.path)
        formatted_history = [{"user": u, "assistant": a} for u, a in chat_history]

        # Contextualize question
        standalone_questions = contextualize_question(
            formatted_history, 
            user_input, 
            company_name=self.company_name
        )

        context = [
            self.query_core_data(query=question, lang=standalone_questions["lang"])
            for question in standalone_questions["text"][0] if question
        ] if standalone_questions["requires_db"] else []

        full_response = "".join(answer_question(context, standalone_questions["text"], user_input, company_name=self.company_name))
        yield full_response

        append_to_session_history(session_id, user_input, full_response, path=self.client.path)
        self.client.close()

        print(f"Total processing time: {time.time() - start_time:.2f} seconds")
