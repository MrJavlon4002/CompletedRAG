from app.views import ModelViewset
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.conf.urls.static import static

from core import settings
router = DefaultRouter()
router.register("model", ModelViewset, basename='model')
urlpatterns = [
    path('', include(router.urls)),  
]

