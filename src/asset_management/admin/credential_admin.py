from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.utils.html import format_html

from asset_management.models import Credential, CredentialCategory
from config.widgets.mw_select_multiple import UserFilteredSelectMultiple
from employee.models import Employee


@admin.register(CredentialCategory)
class CredentialCategoryAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


class CredentialAdminForm(forms.ModelForm):
    queryset = User.objects.filter(
        employee__active=True, is_superuser=False
    ).select_related("employee")
    privileges = forms.ModelMultipleChoiceField(
        required=False,
        queryset=queryset,
        widget=UserFilteredSelectMultiple(verbose_name="privileges", is_stacked=False),
    )

    class Meta:
        model = Credential
        fields = "__all__"


class CredentialEmployeeFilter(admin.SimpleListFilter):
    title = "Employee"
    parameter_name = "privileges__employee__id"

    def lookups(self, request, model_admin):
        objs = Employee.objects.filter(active=True)
        lookups = [
            (
                emp.id,
                emp.full_name,
            )
            for emp in objs
        ]
        return tuple(lookups)

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            return queryset.filter(privileges__employee__id=value)
        return queryset


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "created_by",
        "access_count",
        "status_col",
    )
    form = CredentialAdminForm
    list_filter = (
        "category",
        "status",
        CredentialEmployeeFilter,
    )
    search_fields = (
        "title",
        "description",
        "privileges__employee__full_name",
    )
    actions = [
        "mark_as_active",
        "mark_as_inactive",
    ]
    change_form_template = "admin/credentials/change_form.html"
    list_select_related = ("category", "created_by")
    list_per_page = 30

    def get_queryset(self, request):
        query_set = (
            super(CredentialAdmin, self)
            .get_queryset(request)
            .select_related("category")
            .prefetch_related(
                Prefetch(
                    "privileges",
                    queryset=User.objects.select_related("employee"),
                    to_attr="all_privileges",
                )
            )
        )
        if not request.user.is_superuser and not request.user.has_perm(
            "asset_management.access_all_credentials"
        ):
            return query_set.filter(privileges__in=[request.user])
        return query_set

    @admin.display(description="Total Privileges")
    def access_count(self, obj: Credential):
        data = getattr(obj, "all_privileges", [])
        return len(data)

    @admin.action(description="Mark as Active")
    def mark_as_active(self, request, queryset):
        if request.user.is_superuser:
            queryset.update(status="ACTIVE")

    @admin.action(description="Mark as InActive")
    def mark_as_inactive(self, request, queryset):
        if request.user.is_superuser:
            queryset.update(status="INACTIVE")

    @admin.display(description="Status")
    def status_col(self, obj):
        color = "green"
        if obj.status == "INACTIVE":
            color = "red"
        return format_html(f'<b style="color: {color}">{obj.get_status_display()}</b>')
