from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    # auth (we'll create signup next)
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", include("dashboard.urls")),
    path("favorites/", include("favorites.urls")),
    path("", include("accounts.urls")),
]
