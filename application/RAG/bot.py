from RAG.bot_parts.document_hendler import DocumentHandler
from django.conf import settings

WCD_URL = ''
WCD_API_KEY = ''
DATA_PATH = settings.DATA_PATH


CHUNK_SIZE = 1000
OVERLAP_CHUNKS = 5 # 5 sentence overlap



def ask(session_id, user_input, company_name, lang):
    doc_handler = DocumentHandler(db_url=WCD_URL, db_api_key=WCD_API_KEY, company_name=company_name,path=DATA_PATH, chunk_overlap=OVERLAP_CHUNKS, chunk_size=CHUNK_SIZE)
    for part in doc_handler.ask_question(session_id=session_id, user_input=user_input, lang=lang):
        yield part