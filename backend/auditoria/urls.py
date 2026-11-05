from django.urls import path
from . import views

urlpatterns = [
    path('historial/', views.HistorialListView.as_view(), name='historial-list'),
    path('historial/<int:pk>/', views.HistorialDetailView.as_view(), name='historial-detail'),
]