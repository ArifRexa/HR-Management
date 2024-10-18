from django.contrib import admin
from .models import Agenda, Reception
from django.utils.html import format_html
from django.utils import timezone

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    pass

    def has_module_permission(self, request):
        return False

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('get_time','get_status','name','agenda_name' ,'get_short_comment', 'get_created_date')
    list_filter = ('status',)
    date_hierarchy = 'created_at'  
    actions = ['approve_status','pending_status']  
    class Media:
        js = ("js/reception.js",)  # Ensure this is correct
        css = {
            'all': ('css/reception.css',)  # Adjust the path as needed
        }

    def get_short_comment(self, obj):
        # Show the first 3-4 words of the comment
        short_comment = ' '.join(obj.comment.split()[:3]) + '...' if obj.comment else ''
        print(short_comment)
        return format_html(
            '<span class="comment-popup" data-full-comment="{}">{}</span>',
            obj.comment, short_comment
        )

    get_short_comment.short_description = 'Comment'

    def get_time(self, obj):
        # Format the naive datetime directly in 12-hour format with AM/PM
        time_formatted = obj.created_at.strftime('%I:%M%p').lower()
        return time_formatted
    
    get_time.short_description = 'Time'

    def get_created_date(self, obj):
        # Format the date only (YYYY-MM-DD)
        return obj.created_at.strftime('%Y-%m-%d')

    get_created_date.short_description = 'Created Date'
    get_created_date.admin_order_field = 'created_at'


    def get_status(self, obj):
        if obj.status == 'pending':
            return format_html('<span style="color: red;">{}</span>', obj.get_status_display())
        else:
            return format_html('<span style="color: green;">{}</span>', obj.get_status_display())

    get_status.short_description = 'Status'
    

    @admin.action(description="Mark as approve")
    def approve_status(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Mark as pending")
    def pending_status(self, request, queryset):
        queryset.update(status='pending')
