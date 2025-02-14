from RAG.bot_parts.document_hendler import DocumentHandler
from django.conf import settings

# WCD_URL = settings.WCD_URL
# WCD_API_KEY = settings.WCD_API_KEY
# COMPANY_NAME = settings.COMPANY_NAME

WCD_URL = 'https://yluukv1xqra0g8jo9pyxdw.c0.asia-southeast1.gcp.weaviate.cloud'
WCD_API_KEY = '8E8uvXYmEYv3FJlZ9RQvQvBCdYS7VGmR60KF'
COMPANY_NAME = "Aisha"

DATA_PATH = "/app/RAG"



CHUNK_SIZE = 1000
OVERLAP_CHUNKS = 400



def ask(session_id, user_input, company_name):
    doc_handler = DocumentHandler(db_url=WCD_URL, db_api_key=WCD_API_KEY, company_name=COMPANY_NAME,path=DATA_PATH, chunk_overlap=OVERLAP_CHUNKS, chunk_size=CHUNK_SIZE)
    for part in doc_handler.ask_question(session_id=session_id, user_input=user_input):
        yield part