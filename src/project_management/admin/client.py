from django.contrib import admin
from django.utils.html import format_html
from project_management.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "get_project_name",
        "email",
        "linkedin_url",
        "country",
        "address",
    )
    fields = (
        "name",
        "email",
        "logo",
        "client_feedback",
        "image",
        "linkedin_url",
        "cc_email",
        "address",
        "country",
        "notes",
    )

    @admin.display(description="Project Name")
    def get_project_name(self, obj):
        project_name = obj.project_set.all().values_list("title", flat=True)

        return format_html("<br>".join(project_name))

    # get_project_name.short_description = "Project Name"

    def has_module_permission(self, request):
        return False
