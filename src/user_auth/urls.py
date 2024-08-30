from django.urls import path
from django.contrib.auth import views as auth_views
from .views import verify_otp, CustomAdminLoginView

urlpatterns = [
    path('admin/login/', CustomAdminLoginView.as_view(), name='admin_login'),
    path('admin/verify-otp/', verify_otp, name='verify_otp'),
]