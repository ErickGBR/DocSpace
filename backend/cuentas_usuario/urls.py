from django.urls import path, re_path
from .views import LoginView, LogoutView, RefreshView, RegisterView

urlpatterns = [
    re_path(r'^auth/register/?$', RegisterView.as_view(), name='auth-register'),
    re_path(r'^auth/login/?$', LoginView.as_view(), name='auth-login'),
    re_path(r'^auth/refresh/?$', RefreshView.as_view(), name='auth-refresh'),
    re_path(r'^auth/logout/?$', LogoutView.as_view(), name='auth-logout'),
]