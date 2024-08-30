from django.contrib import admin
from .models import UserLogs
# Register your models here.
from django.contrib.sessions.models import Session
from django.utils import timezone

@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'designation', 'loging_time')
    search_fields = ('name', 'email', 'designation')
    list_filter = ('loging_time', 'user')
    ordering = ('-loging_time',)
    actions = ['logout_selected_users']
    
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