from ast import List
import re
from django.contrib import admin
from django.utils.html import format_html
# from networkx import project
from project_management.models import Client,ClientInvoiceDate,Project, Technology
from django.utils.translation import gettext_lazy as _




class ClientInvoiceDateInline(admin.StackedInline):
    model = ClientInvoiceDate
    extra = 1


class ActiveProjectFilter(admin.SimpleListFilter):
    title = _('Active Project')
    parameter_name = 'active_project'

    def lookups(self, request, model_admin):
        project_title = Project.objects.filter(active=True).values_list('title',flat=True)
        return tuple([(title,title) for title in project_title])

    def queryset(self, request, queryset):
        qs = queryset.filter(project__title = request.GET.get(self.parameter_name))
        return qs


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
        "bill_from",
        "cc_email",
        "address",
        "country",
        "notes",
        "is_hour_breakdown",
    )
    list_filter = ("project__active",)
    inlines = (ClientInvoiceDateInline,)
    search_fields = ['name']
    @admin.display(description="Project Name")
    def get_project_name(self, obj):
        project_name = obj.project_set.all().values_list("title", flat=True)

        return format_html("<br>".join(project_name))

    # get_project_name.short_description = "Project Name"

    def has_module_permission(self, request):
        return False
