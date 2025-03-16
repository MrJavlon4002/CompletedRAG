from app.views import ModelViewset, get_session_history, insert_data
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.conf.urls.static import static

from core import settings
router = DefaultRouter()
router.register("model", ModelViewset, basename='model')
urlpatterns = [
    path('', include(router.urls)),
    path('history/<int:session_id>/', get_session_history),
    path('history/<int:session_id>/append/', insert_data)
]

