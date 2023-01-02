from django.contrib import admin

from asset_management.models.contact import Contact, Profession


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    search_fields = ('name', 'profession__title', 'phone')
    list_display = ('name', 'profession', 'phone', 'address')
    list_filter = ('profession',)

    def has_module_permission(self, request):
        return False
