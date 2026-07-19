from django.urls import path

from .views import profile_view, toggle_theme, SignupView


app_name = "accounts"

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("theme/", toggle_theme, name="toggle_theme"),
]
