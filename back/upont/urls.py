"""upont URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("login/", views.login),
    path("social/", include("social.urls")),
    path("admin/", admin.site.urls),
    path('login/', views.Login.as_view(), name="login"),
    path('password_change/', views.PasswordChange.as_view(), name="password_change"),
    path('password_change_done/', views.PasswordChangeDone.as_view(), name="password_change_done"),
    path('password_reset_form/', views.PasswordReset.as_view(), name="password_reset_form"),
    path('password_reset_done/', views.PasswordResetDone.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path('password_reset_complete/', views.PasswordResetComplete.as_view(), name="password_reset_complete"),
]

# Only for dev, gives anyone access to any image
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
