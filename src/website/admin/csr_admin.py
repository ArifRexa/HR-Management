from django.contrib import admin
from django.http import HttpRequest
from website.csr_models import CSR, OurEvent, OurEffort

# Define inline classes for OurEvent and OurEffort
class OurEventInline(admin.StackedInline):
    model = OurEvent
    extra = 1  # Number of inline forms to display

class OurEffortInline(admin.StackedInline):
    model = OurEffort
    extra = 1  # Number of inline forms to display

# Define CSR admin
@admin.register(CSR)
class CSRAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')  # Customize the display columns in the list view
    inlines = [OurEventInline, OurEffortInline]  # Inline OurEvent and OurEffort models


    def has_module_permission(self, request):
        return False