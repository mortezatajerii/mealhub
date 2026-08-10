from django.urls import path
from .views import LoginView, LogoutView, RegisterView, MeView
from .template_views import (
    LoginTemplateView,
    RegisterTemplateView,
    DashboardTemplateView,
    logout_view,
)

app_name = "accounts"

# API endpoints (existing)
api_patterns = [
    path("auth/login/", LoginView.as_view(), name="api_login"),
    path("auth/logout/", LogoutView.as_view(), name="api_logout"),
    path("auth/register/", RegisterView.as_view(), name="api_register"),
    path("me/", MeView.as_view(), name="api_me"),
]

# Template-based endpoints (new)
template_patterns = [
    path("login/", LoginTemplateView.as_view(), name="login"),
    path("register/", RegisterTemplateView.as_view(), name="register"),
    path("dashboard/", DashboardTemplateView.as_view(), name="dashboard"),
    # path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
    path("logout/", logout_view, name="logout"),
]

urlpatterns = api_patterns + template_patterns
