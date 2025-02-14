from rest_framework import serializers
from app.models import Model

class ModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ['company_name', 'session_id', 'user_input']