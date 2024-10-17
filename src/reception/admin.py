from django.contrib import admin
from .models import Reception
from django.utils.html import format_html

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'agenda', 'get_comment', 'created_at', 'get_status')
    list_filter = ('status', 'agenda')
    date_hierarchy = 'created_at'  
    actions = ['approve_status','pending_status']  
    class Media:
        js = ("js/reception.js",)

    def get_comment(self, obj):
        if obj.comment:
            truncated_comment = ' '.join(obj.comment.split()[:4]) + '...'
            return format_html('<span title="{}">{}</span>', obj.comment, truncated_comment)
        return '-'
    
    get_comment.short_description = 'Comment'

    def get_status(self, obj):
        if obj.status == 'pending':
            return format_html('<span style="color: red;">{}</span>', obj.get_status_display())
        else:
            return format_html('<span style="color: green;">{}</span>', obj.get_status_display())
        
    @admin.action(description="Approve all selected receptions")
    def approve_status(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Pending all selected receptions")
    def pending_status(self, request, queryset):
        queryset.update(status='pending')
