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
from django.urls import path, include
from core.views import Login, ProfileViewSet, \
    LogoutView, ProfileSearchListView, ResetPassword, \
    CategoryViewSet, SubCategoryViewSet, ChildSubCategoryViewSet, GoogleSignViewSet, VerifyEmail, ForgotPassword

router = DefaultRouter(trailing_slash=False)
router.register(r'signup', ProfileViewSet)
router.register(r'google_login', GoogleSignViewSet)
router.register(r'search', ProfileSearchListView)
router.register(r'category', CategoryViewSet)
router.register(r'subcategory', SubCategoryViewSet)
router.register(r'child_subcategory', ChildSubCategoryViewSet)
router.register(r'fuzzysearch', views.FuzzySearchView)
urlpatterns = router.urls

urlpatterns = [
    path('login/', Login.as_view(), name='log_in'),
    path("profile-update/<str:pk>/", views.UpdateProfileViewSet.as_view({
        "put": "update",
    }
    ), name="profile_update", ),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('accounts/', include('allauth.urls')),
    path('microsoft/', include('microsoft_auth.urls', namespace='microsoft')),
    path('social-auth/', include('social_django.urls', namespace="social")),
    path('reset-password/', ResetPassword.as_view(), name='reset_password'),

    path('verify-email/', VerifyEmail.as_view({"get": "get_user_data"}), name='verify_email'),
    path('forgot-password/', views.ForgotPassword.as_view({
        "post": "get_email"
    }), name="forgot_password"),
]
urlpatterns += router.urls
