from app.models import Model
from app.serializers import ModelSerializers
from rest_framework import viewsets,status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from RAG.bot import ask


class ModelViewset(viewsets.ViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializers
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        session_id = request.data.get("session_id")
        user_input = request.data.get("user_input")
        company_name = request.data.get("company_name", "Aisha")  
        if not session_id or not user_input:
            return Response({"error": "session_id va user_input talab qilinadi"}, status=status.HTTP_400_BAD_REQUEST)

        response_data = []
        for part in ask(session_id=session_id, user_input=user_input, company_name=company_name):
            print(part)
            response_data.append(part)

        return Response({"response": response_data}, status=status.HTTP_200_OK)

    

