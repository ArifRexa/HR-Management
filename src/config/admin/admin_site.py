from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {
                'app_list': []
            }
        return super().index(request, extra_context)
