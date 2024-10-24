from django.contrib import admin
from .models import Agenda, Reception
from django.utils.html import format_html

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('get_time', 'get_status', 'name', 'agenda_name', 'get_short_comment', 'approved_by', 'get_created_date')
    list_filter = ('status', 'agenda_name')
    date_hierarchy = 'created_at'  
    actions = ['approve_status', 'pending_status']  
    change_list_template = "reception.html"
    readonly_fields = ["approved_by"]

    class Media:
        js = ("js/reception.js",)  # Ensure this is correct
        css = {
            'all': ('css/reception.css',)  # Adjust the path as needed
        }

    def save_model(self, request, obj, *args, **kwargs):
        """Save the model instance with updated approved_by if necessary."""
        # If the status is being set to 'approved', assign the approved_by field
        if obj.status == 'approved':
            obj.approved_by = request.user.employee.full_name
        
        # Call the parent class's save_model method to save the instance
        super().save_model(request, obj, *args, **kwargs)

    def get_short_comment(self, obj):
        """Show a shortened version of the comment."""
        short_comment = ' '.join(obj.comment.split()[:3]) + '...' if obj.comment else ''
        return format_html(
            '<span class="comment-popup" data-full-comment="{}">{}</span>',
            obj.comment, short_comment
        )

    get_short_comment.short_description = 'Comment'

    def get_time(self, obj):
        """Format the created_at time in 12-hour format."""
        return obj.created_at.strftime('%I:%M%p').lower()
    
    get_time.short_description = 'Time'

    def get_created_date(self, obj):
        """Return the created date in YYYY-MM-DD format."""
        return obj.created_at.strftime('%Y-%m-%d')

    get_created_date.short_description = 'Created Date'
    get_created_date.admin_order_field = 'created_at'

    def get_status(self, obj):
        """Format the status with color coding."""
        if obj.status == 'pending':
            return format_html('<span style="color: red;">{}</span>', obj.get_status_display())
        else:
            return format_html('<span style="color: green;">{}</span>', obj.get_status_display())

    get_status.short_description = 'Status'
    
    @admin.action(description="Mark as approved")
    def approve_status(self, request, queryset):
        """Bulk action to approve selected receptions."""
        queryset.update(status='approved')
        for reception in queryset:
            reception.approved_by = request.user.employee.full_name  # Optionally set approved_by
            reception.save()

    @admin.action(description="Mark as pending")
    def pending_status(self, request, queryset):
        """Bulk action to set selected receptions back to pending."""
        queryset.update(status='pending', approved_by=None)  # Optionally reset approved_by
