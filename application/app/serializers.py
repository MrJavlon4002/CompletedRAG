from rest_framework import serializers
from app.models import Model

class ModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = "__all__"