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
from rest_framework.routers import DefaultRouter
from core import views
from django.urls import path, include
from core.views import Login, ProfileViewSet, \
    LogoutView, ProfileSearchListView, ResetPassword, \
    CategoryViewSet, SubCategoryViewSet, ChildSubCategoryViewSet, \
    GoogleSignViewSet, VerifyEmail, SendVerificationEmail
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter(trailing_slash=False)
router.register(r'signup', ProfileViewSet)
router.register(r'send_verification_email', SendVerificationEmail)

router.register(r'google_login', GoogleSignViewSet)
router.register(r'search', ProfileSearchListView)
router.register(r'category', CategoryViewSet)
router.register(r'subcategory', SubCategoryViewSet)
router.register(r'child_subcategory', ChildSubCategoryViewSet)
router.register(r'fuzzysearch', views.FuzzySearchView)
router.register(r'add_product', views.AddProductView)
# router.register(r'add_links', views.AddSocialLinksView)
router.register(r'add_service', views.AddServiesView)

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
    path('add-publication/', views.PublicationView.as_view({
        "post": "create"
    }), name="add_publication"),
    path('get-publication/', views.PublicationView.as_view({
        "get": "list"
    }), name="get_publication"),
    path('save-supplier/', views.SaveSupplierView.as_view({
        "post": "create", "get": "list"
    }), name="save_supplier"),
    path('get_prod_data/', views.GetSpecificProd.as_view({
        "get": "list"
    }), name="get-prod-data"),
    path('add_links/', views.AddSocialLinksView.as_view({
        "post": "create"
    }), name="add-links"),
    path('get_links/', views.AddSocialLinksView.as_view({
        "get": "list"
    }), name="get-links"),
    path('update_links/<str:pk>/', views.AddSocialLinksView.as_view({
        "put": "update"
    }), name="update-links"),
]
urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
