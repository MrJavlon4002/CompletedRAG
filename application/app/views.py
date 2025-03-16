import sqlite3
from app.models import Model
from app.serializers import ModelSerializers
from rest_framework import viewsets,status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view
from RAG.bot import ask
from RAG.bot_parts.query_redis import append_to_session_history, get_redis_session_history
from core.settings import DATA_PATH

class ModelViewset(viewsets.ModelViewSet):
    queryset = Model.objects.all().order_by("id") 
    serializer_class = ModelSerializers
    permission_classes = [AllowAny]

    def get_queryset(self):
        """GET requestlar uchun barcha Model obyektlarini qaytarish."""
        return Model.objects.all()

    def create(self, request, *args, **kwargs):
        """Foydalanuvchi yangi model yaratishi uchun `POST` method."""
        session_id = request.data.get("session_id")
        user_input = request.data.get("user_input")
        company_name = request.data.get("company_name")  

        if not session_id or not user_input:
            return Response({"error": "session_id va user_input talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []
        for part in ask(session_id=session_id, user_input=user_input, company_name=company_name):
            response_data.append(part)

        return Response({"response": response_data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """PUT methodni taqiqlash."""
        return Response({"error": "PUT methodga ruxsat yo'q"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        """PATCH methodni taqiqlash."""
        return Response({"error": "PATCH methodga ruxsat yo'q"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        """DELETE methodni taqiqlash."""
        return Response({"error": "DELETE methodga ruxsat yo'q"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    

@api_view(['GET'])
def get_session_history(r, session_id: str):
    # print(DATA_PATH+"/chat_history.db")
    history = get_redis_session_history(session_id)
    print(history)
    return Response({"history": history})

@api_view(['POST'])
def insert_data(r, session_id: str):
    append_to_session_history(session_id=session_id, user_input=r.data['user_input'], assistant_response=r.data['assistant_response'])
    return Response({"ok": True})
