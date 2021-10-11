"""rfx_backend URL Configuration

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
import rest_framework
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from core import views
from django.urls import include
from core.views import log_in, ProfileViewSet, LogoutView, ProfileSearchListView

router = DefaultRouter(trailing_slash=False)
router.register(r'signup', ProfileViewSet)
router.register(r'search', ProfileSearchListView)
urlpatterns = router.urls

urlpatterns = [
    path('login/', log_in.as_view(), name='log_in'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
urlpatterns += router.urls
