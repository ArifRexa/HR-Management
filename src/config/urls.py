"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib.auth import views as auth_view
from django.shortcuts import redirect
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from rest_framework.schemas import get_schema_view

from employee.admin.employee.extra_url.formal_view import EmployeeNearbySummery

admin.site.site_header = settings.APP_SITE_HEADER
admin.site.site_title = settings.APP_SITE_TITLE
admin.site.index_title = settings.APP_INDEX_TITLE

employee_formal_summery = EmployeeNearbySummery()

extra_context = dict(
    leaves=employee_formal_summery.employee_leave_nearby,
    birthdays=employee_formal_summery.birthdays,
    increments=employee_formal_summery.increments,
    permanents=employee_formal_summery.permanents,
    anniversaries=employee_formal_summery.anniversaries
)

urlpatterns = [
    path('', include('job_board.urls')),
    path('', include('website.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('settings/', include('settings.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='js-catalog'),
    # path('admin/account/', include('account.urls')),
    path('admin/', admin.site.urls, {'extra_context': extra_context}),

    path("password-change/", auth_view.PasswordChangeView.as_view(extra_context=extra_context), name='password_change'),
    path("password-change/done/", auth_view.PasswordResetDoneView.as_view(), name='password_change_done'),

    path('password-reset/', auth_view.PasswordResetView.as_view(), name="admin_password_reset"),
    path('password-reset/done/', auth_view.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_view.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('tinymce/', include('tinymce.urls')),

    path('openapi', get_schema_view(
        title="Mediusware Ltd",
        description="API for all …",
        version="1.0.0"
    ), name='openapi-schema'),

    path('all-api-doc/', TemplateView.as_view(
        template_name='docs/swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),

    path('', lambda request: redirect('/admin')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
