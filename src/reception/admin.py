from django.contrib import admin
from .models import Agenda, Reception
from django.utils.html import format_html
from datetime import datetime

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    pass

@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('get_time','name','agenda_name' ,'get_comment', 'get_date', 'get_status')
    list_filter = ('status',)
    date_hierarchy = 'created_at'  
    actions = ['approve_status','pending_status']  
    class Media:
        js = ("js/reception.js",)

    def get_date(self,obj):   
        datetime_str = datetime.strptime(str(obj.created_at), '%Y-%m-%d %H:%M:%S.%f')
        print(datetime_str.time())
        return datetime_str.date()
    
    get_date.short_description = 'Date'

    def get_time(self,obj):
        time_str = datetime.strptime(str(obj.created_at), '%Y-%m-%d %H:%M:%S.%f').time()
        return time_str.strftime('%H:%M:%S')
    get_time.short_description = 'Entry Time'

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
    

    @admin.action(description="Mark as approve")
    def approve_status(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description="Mark as pending")
    def pending_status(self, request, queryset):
        queryset.update(status='pending')
