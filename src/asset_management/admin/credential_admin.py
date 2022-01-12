from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

from asset_management.models import CredentialCategory, Credential


@admin.register(CredentialCategory)
class CredentialCategoryAdmin(admin.ModelAdmin):
    pass


class CredentialAdminForm(forms.ModelForm):
    queryset = User.objects.filter(employee__active=True, is_superuser=False)
    privileges = forms.ModelMultipleChoiceField(
        required=False,
        queryset=queryset,
        widget=FilteredSelectMultiple(verbose_name='privileges', is_stacked=False))

    class Meta:
        model = Credential
        fields = "__all__"


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_by', 'access_count')
    form = CredentialAdminForm
    list_filter = ('category',)
    search_fields = ('title', 'description')
    change_form_template = 'admin/credentials/change_form.html'


    def get_queryset(self, request):
        query_set = super(CredentialAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return query_set.filter(privileges__in=[request.user])
        return query_set

    @admin.display(description='Total Privileges')
    def access_count(self, obj: Credential):
        return obj.privileges.count()
