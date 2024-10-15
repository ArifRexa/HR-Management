from django.contrib import admin
from .models import Reception
from django.utils.html import format_html

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'agenda','get_comment','created_at','status')
    list_filter = ('agenda','status','created_at')
    date_hierarchy = ('created_at')
    def get_comment(self, obj):
        if obj.comment:
            truncated_comment = ' '.join(obj.comment.split()[:4]) + '...'
            return format_html('<span title="{}">{}</span>', obj.comment, truncated_comment)
        return '-'

    get_comment.short_description = 'Comment'