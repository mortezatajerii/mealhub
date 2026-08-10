from django.urls import path
from .views import LoginView, LogoutView, RegisterView, MeView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth_login"),
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),
    path("auth/register/", RegisterView.as_view(), name="auth_register"),
    path("me/", MeView.as_view(), name="me"),
]
