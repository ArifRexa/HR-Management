from django.contrib import admin
from .models import Reception
from django.utils.html import format_html

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'agenda','get_comment','created_at','get_status')
    list_filter = ('status','agenda')
    date_hierarchy = ('created_at')

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

    get_status.short_description = 'Status'