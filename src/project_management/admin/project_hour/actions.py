from django.contrib import admin


class ProjectHourAction(admin.ModelAdmin):
    actions = ['export_as_csv', 'enable_payable_status', 'disable_payable_status']

    def get_actions(self, request):
        actions = super().get_actions(request)
        print(actions['export_as_csv'])
        if not request.user.is_superuser:
            del actions['enable_payable_status']
            del actions['disable_payable_status']
        return actions

    @admin.action()
    def enable_payable_status(self, request, queryset):
        queryset.update(payable=True)

    @admin.action()
    def disable_payable_status(self, request, queryset):
        queryset.update(payable=False)

    @admin.action()
    def export_as_csv(self, request, queryset):
        pass
