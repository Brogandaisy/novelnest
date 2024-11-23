"""
URL configuration for novelnest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from books.views import signup
from books.views import about, homepage
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from books.views import about
from django.contrib.auth import views as auth_views




urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/password-change/", PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password-change/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("accounts/", include("django.contrib.auth.urls")),  # Include other auth URLs
    path("accounts/profile/", auth_views.TemplateView.as_view(template_name='accounts/profile.html'), name='account'),
    path("signup/", signup, name="signup"),
    path("books/", include("books.urls")),  # Keep books-related URLs here
    path("about/", about, name="about"),
    path("", homepage, name="homepage"),
]
