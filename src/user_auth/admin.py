from django.contrib import admin
from .models import UserLogs
# Register your models here.
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.admin.filters import RelatedOnlyFieldListFilter

class ActiveUserOnlyFilter(RelatedOnlyFieldListFilter):
    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False, limit_choices_to={'is_active': True})

@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ('user_info','location','device_name','browser_name','loging_time')
    search_fields = ('name', 'email', 'designation')
    list_filter = ('loging_time', ('user', ActiveUserOnlyFilter))
    ordering = ('-loging_time',)
    actions = ['logout_selected_users']
    
    def user_info(self, obj):
        user = obj.user
        # Safely format the HTML with format_html
        return format_html(
            'Name: {} {}<br>'
            'Email: {}<br>'
            'Designation: {}',
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