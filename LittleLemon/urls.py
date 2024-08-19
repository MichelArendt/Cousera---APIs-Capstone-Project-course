"""
URL configuration for LittleLemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.views.decorators.csrf import csrf_exempt

import API.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(API.urls)),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('token/login/', csrf_exempt(RedirectView.as_view(url='/api/token/login/', permanent=True))), # Redirect /token/login/ to /api/token/login/
    path('api/users/users/me/', csrf_exempt(RedirectView.as_view(url='/api/users/me/', permanent=True))), # Redirect api/users/users/me/ to /api/users/me/
]
