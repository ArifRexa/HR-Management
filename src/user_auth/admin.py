from django.contrib import admin
from .models import UserLogs
# Register your models here.
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.admin.filters import RelatedOnlyFieldListFilter
from django.db.models import Q
class ActiveUserOnlyFilter(RelatedOnlyFieldListFilter):
    def field_choices(self, field, request, model_admin):
        # Fetch users with first_name and last_name
        users = field.related_model.objects.filter(
            Q(first_name__isnull=False) & Q(last_name__isnull=False)
        ).distinct()

        # Generate choices based on first_name and last_name
        choices = [(user.id, f'{user.first_name} {user.last_name}') for user in users]
        
        return [(None, 'All')] + choices
    
class ActiveUserFilter(admin.SimpleListFilter):
    title = 'currently logged in'
    parameter_name = 'currently_logged_in'

    def lookups(self, request, model_admin):
        return (
            ('Logged Users', 'Logged Users'),
            ('Logout Users', 'Logout Users'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Logged Users':
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            active_user_ids = [session.get_decoded().get('_auth_user_id') for session in active_sessions]
            return queryset.filter(user__id__in=active_user_ids)
        elif self.value() == 'Logout Users':
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            active_user_ids = [session.get_decoded().get('_auth_user_id') for session in active_sessions]
            return queryset.exclude(user__id__in=active_user_ids)
        return queryset

@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ('user_info','location','device_name','operating_system','browser_name','ip_address','loging_time')
    search_fields = ('name', 'email', 'designation')
    list_filter = (ActiveUserFilter,'loging_time', ('user', ActiveUserOnlyFilter))
    ordering = ('-loging_time',)
    actions = ['logout_selected_users']
    
    def user_info(self, obj):
        user = obj.user
        # Safely format the HTML with format_html and remove boldness from email and designation
        return format_html(
            '{} {}<br>'
            '<span style="font-weight: normal;">{}</span><br>'
            '<span style="font-weight: normal;">{}</span>',
            user.first_name, user.last_name,
            user.email,
            getattr(user.employee.designation, 'title', 'Not Available')
        )
    user_info.short_description = 'User Info'

    def logout_selected_users(self, request, queryset):
        for log in queryset:
            # Get all sessions
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            for session in sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(log.user.id):
                    session.delete()  # Log out the user by deleting the session

        self.message_user(request, f"Selected users have been logged out.")
    
    logout_selected_users.short_description = "Logout selected users"