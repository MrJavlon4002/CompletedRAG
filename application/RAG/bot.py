from RAG.bot_parts.document_hendler import DocumentHandler
from django.conf import settings

DATA_PATH = settings.DATA_PATH
WCD_URL = settings.WCD_URL
WCD_API_KEY = settings.WCD_API_KEY
COMPANY_NAME = settings.COMPANY_NAME

DATA_PATH = "/application/RAG"



CHUNK_SIZE = 1000
OVERLAP_CHUNKS = 400



def ask(session_id, user_input, company_name):
    doc_handler = DocumentHandler(db_url=WCD_URL, db_api_key=WCD_API_KEY, company_name=COMPANY_NAME,path=DATA_PATH, chunk_overlap=OVERLAP_CHUNKS, chunk_size=CHUNK_SIZE)
    for part in doc_handler.ask_question(session_id=session_id, user_input=user_input):
        yield part