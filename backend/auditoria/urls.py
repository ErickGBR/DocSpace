from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistorialViewSet

router = DefaultRouter()
router.register(r'historial', HistorialViewSet, basename='historial')

urlpatterns = [
    path('', include(router.urls)),
]
