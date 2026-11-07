from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EspacioTrabajoViewSet

router = DefaultRouter()
router.register(r'espacios', EspacioTrabajoViewSet, basename='espacio-trabajo')

urlpatterns = [
    path('', include(router.urls)),
]